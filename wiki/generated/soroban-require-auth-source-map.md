# Generated source map: Soroban require_auth

> POC 手写生成层示例。后续如果增加 `export-wiki` CLI，本页应由 JSON 自动生成。不要把本页当作事实源手工扩写。

## Primary pattern

- id: `soroban-require-auth-entrypoint-bypass-pattern`
- path: `data/normalized/vulnerability_patterns/soroban-require-auth-entrypoint-bypass-pattern.json`
- category: `access-control`
- language: `rust-soroban`
- linked concept: [[concepts/soroban-require-auth|Soroban require_auth entrypoint 授权绕过]]

## Related cases

### `c4-2025-02-blend-v2-h-02`

- path: `data/normalized/case_reports/c4-2025-02-blend-v2-h-02.json`
- severity: High
- title: User can steal other users' emissions due to vulnerable claim implementation
- source: https://code4rena.com/reports/2025-02-blend-v2-audit-certora-formal-verification#h-02-user-can-steal-other-users-emissions-due-to-vulnerable-claim-implementation
- pinned snippets include:
  - https://github.com/code-423n4/2025-02-blend/blob/f23b3260763488f365ef6a95bfb139c95b0ed0f9/blend-contracts-v2/backstop/src/emissions/distributor.rs#L122-L124
  - https://github.com/code-423n4/2025-02-blend/blob/f23b3260763488f365ef6a95bfb139c95b0ed0f9/blend-contracts-v2/backstop/src/emissions/claim.rs#L66

### `c4-2025-02-blend-v2-m-01`

- path: `data/normalized/case_reports/c4-2025-02-blend-v2-m-01.json`
- severity: Medium
- title: Flash loans allow borrowing from frozen pools, bypassing security controls
- source: https://code4rena.com/reports/2025-02-blend-v2-audit-certora-formal-verification#m-01-flash-loans-allow-borrowing-from-frozen-pools-bypassing-security-controls
- pinned snippets include:
  - https://github.com/code-423n4/2025-02-blend/blob/f23b3260763488f365ef6a95bfb139c95b0ed0f9/blend-contracts-v2/pool/src/pool/submit.rs#L868-L895
  - https://github.com/code-423n4/2025-02-blend/blob/f23b3260763488f365ef6a95bfb139c95b0ed0f9/blend-contracts-v2/pool/src/pool/status.rs#L71

## Caution / false-positive

- id: `soroban-internal-helper-missing-require-auth-fp-01`
- path: `data/normalized/false_positive_cases/soroban-internal-helper-missing-require-auth-fp-01.json`
- linked page: [[concepts/soroban-require-auth-false-positives|常见误报/降级]]

## Validation recipe

- id: `soroban-require-auth-entrypoint-matrix-recipe`
- path: `data/normalized/validation_recipes/soroban-require-auth-entrypoint-matrix-recipe.json`
- linked query: [[queries/triage-soroban-require-auth|Triage 查询模板]]

## Checklist

- id: `k2-soroban-lending-external-report-checklist`
- path: `data/normalized/component_checklists/k2-soroban-lending-external-report-checklist.json`
- relevant invariant: 每个 value-moving 或 config-mutating entrypoint 必须 `require_auth` 正确主体。
