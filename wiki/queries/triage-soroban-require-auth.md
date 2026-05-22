# Triage 查询模板：Soroban require_auth

## 适用场景

用于 Stellar/Soroban Rust 合约中以下候选问题：

- missing `require_auth`
- wrong auth subject
- owner/receiver/caller/invoker 混淆
- alternate entrypoint 绕过主路径授权或 pool status
- claim/withdraw/flash-loan/config 路径权限不一致

相关页面：

- [[concepts/soroban-require-auth|概念页]]
- [[concepts/soroban-require-auth-false-positives|误报/降级]]
- [[generated/soroban-require-auth-source-map|来源索引]]

## audit-rag 查询

直接 issue triage：

```bash
cd /Users/qwe/Audit/audit-rag
source .venv/bin/activate
python -m audit_rag.cli.main triage-issue   "Soroban public entrypoint consumes owner reward/account state but does not require_auth the owner; attacker can pass victim owner and redirect claim"   --ecosystem stellar   --language rust-soroban   --runtime soroban   --strict-runtime
```

活跃审计 lead：

```bash
python -m audit_rag.cli.main add-lead <contest-slug>   "Soroban require_auth owner mismatch in reward claim"   --component soroban-contract   --text "public claim entrypoint accepts owner and receiver; require_auth appears to bind receiver/caller while owner reward state is consumed"

python -m audit_rag.cli.main triage-lead <contest-slug> soroban-require-auth-owner-mismatch-in-reward-claim
python -m audit_rag.cli.main suppress-check <contest-slug> soroban-require-auth-owner-mismatch-in-reward-claim
```

## 当前代码阅读动作

1. 搜索入口：`pub fn`、`#[contractimpl]`、`require_auth`、`Address`。
2. 建表：entrypoint、Address 参数、value-moving 行为、实际授权主体。
3. 标出 owner/account/reward/position 被消费的位置。
4. 对照普通路径和 alternate path：claim、withdraw、borrow、flash-loan、batch submit、callback。
5. 查是否有 pool status / pause / frozen / admin gate 在所有等价路径上一致执行。

## PoC / 单测路线

最小角色：

- `owner`: 有 reward/position/balance。
- `attacker`: 发起交易。
- `receiver`: 接收资产，可等于 attacker。

断言：

- 未经 owner 授权的调用必须失败。
- 如果调用成功，owner 状态不得减少，receiver/attacker 不得收到 owner 的奖励或资产。
- 所有等价入口的授权主体一致。

## HM 成立条件

至少需要：

- public entrypoint 可达。
- attacker 可控制关键 Address 参数或调用顺序。
- 当前路径没有对被消费状态的 owner/account 授权，或授权主体错误。
- 有实际价值转移、限制绕过、核心状态破坏。
- 当前项目代码和历史 case 只是相似证据，不是漏洞证明；必须有当前代码链路或 PoC。

## 降级/停止条件

停止追 Medium/High：

- 只有 internal helper 缺 auth，但所有 public caller 已正确授权。
- 操作 permissionless 且不消费他人状态。
- 只有 admin/test setup 可达。
- 找不到 attacker 控制参数或调用顺序。
- PoC 只能证明 revert 或无影响状态变化。
