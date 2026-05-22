# Soroban require_auth entrypoint 授权绕过

## 一句话定义

在 Soroban/Rust 合约里，敏感动作没有 EVM `msg.sender` 式隐式权限。任何会移动资产、消费用户状态、领取奖励、修改配置的公开 entrypoint，都必须对“被消费状态的正确 Address”执行 `require_auth`。

相关页面：

- [[concepts/soroban-require-auth-false-positives|常见误报/降级]]
- [[queries/triage-soroban-require-auth|Triage 查询模板]]
- [[generated/soroban-require-auth-source-map|来源索引]]

## 为什么重要

这个 bug family 的核心不是“有没有调用 `require_auth`”，而是三件事是否同时成立：

1. 公开 entrypoint 可达。
2. 该入口会消费某个用户/账户/position 的状态，或触发价值转移。
3. 授权主体绑定到了正确的 Address，而不是 receiver、caller、invoker、任意参数或另一个账户。

如果三者任一缺失，通常只能作为检查项或 false-positive 风险，而不是直接报 Medium/High。

## 典型成立条件

- `pub fn` 接收 user/owner/account/receiver 参数。
- 函数会 claim、withdraw、transfer、borrow、flash-loan、改 config、改 pool status、消费 reward/accounting。
- 调用路径中没有对被消费状态的 owner 执行 `require_auth`。
- 或者只在主入口检查，alternate entrypoint / flash-loan / callback / helper path 绕过了同等检查。

## 常见变体

- 奖励领取：攻击者替其他用户 claim emissions/rewards。
- receiver/owner 混淆：对 receiver 授权，但实际消费 owner 的状态。
- alternate entrypoint：主 borrow/withdraw 有检查，flash-loan 或 batch submit 漏掉 pool status/auth。
- callback/hook：外部回调路径绕过前置检查或使用过期检查结果。
- admin/config path：公开入口允许非管理员修改配置。

## 关键 normalized 来源

- Pattern：`soroban-require-auth-entrypoint-bypass-pattern`
  - `data/normalized/vulnerability_patterns/soroban-require-auth-entrypoint-bypass-pattern.json`
- High case：`c4-2025-02-blend-v2-h-02`
  - User can steal other users' emissions due to vulnerable claim implementation
- Medium case：`c4-2025-02-blend-v2-m-01`
  - Flash loans allow borrowing from frozen pools, bypassing security controls
- Recipe：`soroban-require-auth-entrypoint-matrix-recipe`
- Checklist：`k2-soroban-lending-external-report-checklist`

## 审计动作

1. 列出所有 `pub fn`。
2. 标记每个入口是否：转移资产、消费 reward、改 account/position、改 config、绕过 pool status。
3. 对每个入口列出 Address 参数：owner / user / account / receiver / admin / caller。
4. 记录实际执行 `require_auth` 的主体。
5. 建 entrypoint × actor matrix：owner、attacker、receiver、admin、pool、callback recipient。
6. 找出“同样消耗状态但授权主体不同”或“普通路径检查、alternate path 不检查”的入口。
7. 再判断金额、可达性、状态前提和是否已有防护。

## 报告口径

强报告需要说清楚：

- 攻击者调用哪个公开 entrypoint。
- 被消费的是谁的状态。
- 当前代码对谁做了授权，或完全没做授权。
- 为什么该路径可以转移价值或破坏核心状态。
- 影响上限：可盗金额、可绕过的限制、可破坏的协议状态。

## 关联 false-positive

不要只因为 helper 没有 `require_auth` 就报漏洞。先看：

- helper 是否 public entrypoint。
- 所有 public caller 是否已经对同一个 owner/account 授权。
- helper 是否能被 callback / cross-contract path 绕过。

详见：[[concepts/soroban-require-auth-false-positives|Soroban require_auth 常见误报/降级]]。
