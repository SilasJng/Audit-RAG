# Monetrix postmortem: missed final M-01 PM borrow liability

Source report: https://code4rena.com/reports/2026-04-monetrix
Final finding: `[M-01] PM borrow liabilities are omitted from backing, allowing phantom surplus settlement`
Local active repo: `/Users/qwe/Audit/2026-04-monetrix`
Local commit observed: `3d94be1361ca01d959f9165a78f0d75c5657fe3e`
Report commit: `f283eda26272b085de8ece7f8dcee7ffce59b28b`

## What the final report found

The confirmed Medium was not the local `bridgePrincipalFromL1` asynchronous CoreWriter candidate. It was a `totalBackingSigned()` accounting omission:

- `PrecompileReader.suppliedBalance()` reads HyperCore PM/Borrow-Lend 0x811 state but only returns the fourth decoded `supplied` field.
- The same PM state can also contain borrow liabilities.
- `MonetrixAccountant._readL1Backing()` credits supplied USDC / supplied non-USDC notional as positive backing.
- No corresponding PM borrow liability is subtracted.
- `surplus()` and `distributableSurplus()` can therefore be positive while true PM net equity is negative.
- `settleDailyPnL()` Gate 3 can accept phantom surplus, after which `distributeYield()` turns it into minted USDM yield and USDC routing.

Direct local code points:

- `/Users/qwe/Audit/2026-04-monetrix/src/core/PrecompileReader.sol:84-91`
- `/Users/qwe/Audit/2026-04-monetrix/src/core/PrecompileReader.sol:132-162`
- `/Users/qwe/Audit/2026-04-monetrix/src/core/MonetrixAccountant.sol:146-157`
- `/Users/qwe/Audit/2026-04-monetrix/src/core/MonetrixAccountant.sol:180-216`

## Why the local audit missed it

### 1. The right hotspot was identified, but the invariant was incomplete

The local README correctly marked these as highest priority:

- Accountant 4-gate settle pipeline
- HyperCore precompile read semantics
- `totalBackingSigned()` over-report risk

The missed part was the accounting invariant shape. The local invariant wrote PM exposure as:

```text
+ Σ 0x811 supplied USDC / spot × px
```

It did not force the review question:

```text
+ PM supply assets - PM borrow liabilities
```

So the audit checked whether supplied balances are read strictly / converted correctly, but not whether the 0x811 object is a net position or an asset-only field paired with debt fields.

### 2. PM 0x811 review got routed toward activation/revert and bridge availability, not liability semantics

The local notes and tests show `suppliedBalance()` was reviewed, but with the wrong question:

- `test_suppliedBalance_revertsWhenNeverSupplied()` checked fail-closed behavior for never-supplied PM accounts.
- The submitted candidate used PM supplied balance as part of `_sendL1Bridge()` availability.
- The provisional audit-rag pattern captured async action / held-balance / retry accounting.

None of those required decoding the full 0x811 schema or asking: “what are the other three uint64 fields, and are any liabilities?”

### 3. The audit over-indexed on user-visible redemption/bridge flows and under-indexed on Operator settlement as a value-moving sink

The local strongest candidate was a redemption availability bug. That path produced a concrete Foundry PoC, so it consumed attention.

The final report’s path is different:

- normal strategy/PM account enters borrow state;
- `totalBackingSigned()` overstates backing;
- Operator calls normal `settle()`;
- Gate 3 trusts overstated backing;
- yield distribution converts phantom surplus into value movement.

This is not primarily a bridge-finality bug. It is an external-accounting netting bug in the settlement oracle/adapter layer.

### 4. audit-rag had adjacent “vault accounting” knowledge, but not a targeted PM supply-vs-borrow pattern

A current triage query for the exact missed issue returned generic vault/ERC4626/campaign matches, not a direct “external lending position supply-only / debt omitted” case.

The best normalized checklist item was generic:

- `vault accounting must distinguish actual assets from pending, external, or untracked balances`

But there was no strong pattern like:

- external lending/PM account valuation must net supplies and borrows;
- connector/adaptor must decode full asset/liability state, not only positive balances;
- settlement surplus gates must use net equity, not gross collateral.

So audit-rag did not force the missing schema question.

### 5. Trusted-operator suppression pressure probably discouraged the right attack framing

The local notes repeatedly suppressed pure Operator misoperation. That was correct generally, but here the Operator is not the attacker. The bug is contract-side: the on-chain Gate 3 accepts inflated backing even during normal settlement.

Better framing would have been:

- “Operator settlement is bounded by on-chain safety gates.”
- “If a gate’s backing input omits liabilities, a normal Operator action can pass a false safety check.”
- “This is not bad Operator parameters; it is a broken safety oracle/invariant.”

## Concrete process fix

For protocols that count external account balances as backing, add a mandatory adapter schema pass:

1. For every precompile/API reader used in backing, write the full upstream response schema.
2. Classify every field as asset, liability, price, metadata, pending/held, or unknown.
3. For every asset field credited into backing, ask whether a sibling liability field must be subtracted.
4. For every settlement gate, test a negative-equity external account state, not only zero/missing/reverting reads.
5. Add a PoC skeleton where external supply is positive and borrow liability is larger than supply; assert `distributableSurplus()` must be non-positive.

Suggested audit-rag normalized record after curation:

- `external-account-gross-supply-without-borrow-liability-pattern`
- component types: `vault-accounting`, `external-strategy-accounting`, `precompile-reader`, `settlement-gate`
- key invariant: backing/surplus must use net external equity, not gross supply/collateral.
