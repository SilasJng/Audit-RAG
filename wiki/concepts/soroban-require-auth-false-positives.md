# Soroban require_auth 常见误报/降级

## 一句话

`require_auth` 缺失只有在“公开可达 + 消费他人状态/权限 + 授权主体缺失或错误”时才可能成立。内部 helper 没有重复授权，本身通常不是漏洞。

相关页面：

- [[concepts/soroban-require-auth|Soroban require_auth entrypoint 授权绕过]]
- [[queries/triage-soroban-require-auth|Triage 查询模板]]

## normalized 来源

- False-positive：`soroban-internal-helper-missing-require-auth-fp-01`
  - `data/normalized/false_positive_cases/soroban-internal-helper-missing-require-auth-fp-01.json`
- Pattern：`soroban-require-auth-entrypoint-bypass-pattern`

## 为什么看起来危险

Soroban 没有 EVM `msg.sender` 式隐式权限，敏感动作通常要显式 `Address.require_auth`。所以看到某个函数改余额、claim reward、转 token，但函数体里没有 `require_auth`，很容易误判为 High。

## 为什么可能不成立

以下情况通常不能直接报 Medium/High：

1. 函数不是 public entrypoint，只是 internal/private helper。
2. 所有公开调用者已经对同一个被消费状态的 owner/account 做了 `require_auth`。
3. 操作本来就是 permissionless，且不消费他人状态。
4. 参数里的 receiver 只是收款人，不是被扣减状态的 owner。
5. 只能由 admin/test setup 触发，普通攻击者不可达。

## 什么时候又可能是真的

这些信号会把它从“误报风险”拉回真实漏洞：

- 存在另一个公开入口调用 helper，但没有对 owner/account 授权。
- helper 通过 callback、flash-loan、cross-contract path 暴露。
- 代码对 receiver / invoker 授权，但实际扣的是 owner 状态。
- batch submit / alternate operation 与普通路径消耗同一状态，但少了 auth/status gate。
- 测试能用 attacker 作为 invoker，传入 victim owner，并让 victim 状态减少或 reward 被转走。

## 降级/放弃条件

放弃或降级前至少确认：

- 已列出所有 public caller。
- 已确认 caller 对同一 owner/account 授权。
- 没有 callback/cross-contract/flash-loan 可达路径。
- 没有 receiver/owner/caller 参数混淆。
- 没有实际价值移动或核心状态破坏。

如果这些都满足，结论通常是：

- false-positive
- audit checklist item
- QA/Low 风险提示
- needs-entrypoint-reachability，不是 HM finding

## 报告中避免的弱表述

不要写：

- “这个函数没有 require_auth，所以攻击者可以盗取资金。”
- “helper 没有权限检查，因此 High。”

应该写：

- “公开入口 X 可由 attacker 调用，传入 victim 作为 owner；该路径在消费 victim reward 前没有对 victim require_auth；PoC 显示 victim reward 减少且 attacker 收到 token。”

如果没有这条链，就先不要报。
