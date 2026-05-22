# audit-rag Wiki POC

这是 audit-rag 的人读知识层 POC。它不替代 `data/normalized/`、schema、eval、CLI triage，也不作为事实源。

## 当前 POC 主题

- [[concepts/soroban-require-auth|Soroban require_auth entrypoint 授权绕过]]
- [[concepts/soroban-require-auth-false-positives|Soroban require_auth 常见误报/降级]]
- [[queries/triage-soroban-require-auth|Triage 查询模板：Soroban require_auth]]
- [[generated/soroban-require-auth-source-map|生成层示例：Soroban require_auth 来源索引]]
- [[generated/index|Generated normalized index：193 条 normalized 记录]]

## 分层约定

- `generated/`：从 `data/normalized/` 摘出的只读导航页。不要手工维护事实结论。
- `concepts/`：人工/Agent 提炼的概念页，用来解释 bug family、判断路径、跨案例联系。
- `queries/`：可复用审计查询、triage prompt、验证路线。
- `active/`：活跃审计 provisional 笔记。默认低置信，不能直接 promotion。

## Source of truth

正式机器知识仍在：

- `data/normalized/case_reports/`
- `data/normalized/vulnerability_patterns/`
- `data/normalized/false_positive_cases/`
- `data/normalized/component_checklists/`
- `data/normalized/validation_recipes/`
- `data/eval/retrieval_queries.jsonl`

## POC 验收标准

1. 每个概念页必须能追溯到真实 normalized id。
2. false-positive 页必须明确“为什么不成立”。
3. 查询页必须能转成 audit-rag CLI 或审计动作。
4. active audit 内容必须标注 provisional。
5. wiki 不自动反写 `data/normalized/`。
