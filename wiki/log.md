# Wiki POC Log

## 2026-05-22

初始化 audit-rag wiki POC。

选择主题：Soroban `require_auth` / alternate entrypoint 授权绕过。

原因：

- audit-rag 已有 pattern、case、false-positive、validation recipe 和 K2 checklist。
- 这个主题非常适合验证 Obsidian 双链：正向案例、误报、验证路线、K2 借贷 checklist 可以自然互链。
- 对当前多运行时审计方向有复用价值。

本次创建：

- `index.md`
- `SCHEMA.md`
- `log.md`
- `concepts/soroban-require-auth.md`
- `concepts/soroban-require-auth-false-positives.md`
- `queries/triage-soroban-require-auth.md`
- `generated/soroban-require-auth-source-map.md`

下一步候选：

1. 在 `triage-lead` 输出里增加 `related_wiki_pages`，但不要让 wiki 替代检索证据。
2. 增加 wiki lint：broken links、generated 页是否 stale、active 页是否标 provisional。
3. 如果 generated 页面太多，再增加 `export-wiki --only require-auth` 一类过滤参数。

## 2026-05-22 / export-wiki

继续 POC，新增 CLI：

```bash
python -m audit_rag.cli.main export-wiki
```

当前行为：

- 从 `data/normalized/` 读取 case、pattern、false-positive、checklist、recipe、contest note。
- 写入只读 Markdown 到 `wiki/generated/`。
- 生成 `wiki/generated/index.md`。
- 每页保留来源 JSON 路径和 record id。
- generated 页只作为人读导航，不替代 schema/eval/retrieval。

本次导出记录数：193。
