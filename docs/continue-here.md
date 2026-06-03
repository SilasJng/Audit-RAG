# 下次从这里继续（continue-here）

这份文档用于帮助你在关闭窗口、隔天继续、或者换一个新会话时，快速把 audit-rag 项目续上。

## 项目固定信息

- 项目名：audit-rag
- 项目路径：`/Users/qwe/Audit/audit-rag`
- 默认交流语言：中文
- 当前方向：面向竞赛型智能合约审计的线索台账、降级判断和 PoC recipe 工作台；RAG 是知识召回层，不是项目本体
- 第一优先工作流：`lead-ledger` + `candidate-triage` + `suppression-check`

## 下次最推荐的开场方式

你下次直接复制下面任意一种发给我即可。

### 模板 1：最短续接版

```text
继续 audit-rag，项目路径是 /Users/qwe/Audit/audit-rag
```

### 模板 2：标准续接版

```text
继续 audit-rag 项目：
- repo: /Users/qwe/Audit/audit-rag
- 中文交流
- 先检查当前状态
- 先读 docs/prd.md、docs/skill-aware-architecture.md、docs/triage-interface.md
- 然后继续往下做
```

### 模板 3：带任务续接版

```text
继续 audit-rag 项目：
- repo: /Users/qwe/Audit/audit-rag
- 中文交流
- 先检查当前状态
- 先读 docs/skill-aware-architecture.md 和 docs/triage-interface.md
- 然后继续做第二批样本和 validate-data
```

## 我下次进入项目后应该先做什么

如果你没有特别指定，我默认应先做以下步骤：

1. 检查项目目录：`/Users/qwe/Audit/audit-rag`
2. 阅读关键文档：
   - `docs/prd.md`
   - `docs/skill-aware-architecture.md`
   - `docs/triage-interface.md`
   - `docs/week-1-plan.md`
3. 检查当前代码骨架和样本数据
4. 继续当前阶段最自然的下一步

## 当前建议优先级

如果你下次没说具体做什么，建议默认按下面顺序推进：

1. 审计中产生的新 lead 先用 `add-lead` 写入 `data/provisional/contests/<contest-slug>/lead-ledger.jsonl`，不要只散落在对话或 scratch note 里
2. 对非 trivial lead 运行 `triage-lead`，保存 scorecard 到 `data/provisional/contests/<contest-slug>/rag-triage/`
3. 对弱问题、疑似重复或疑似 QA/Low 的 lead 运行 `suppress-check`，优先记录降级/压制理由
4. PoC、duplicate review 或最终判断后运行 `update-lead`，让 ledger 成为 active lead 的唯一状态源
5. 跨会话或阶段复盘时运行 `export-contest-summary`，生成 `contest-summary.md`
6. 维护 `validate-data`、`pytest` 和 retrieval eval 回归，避免正式数据可用性退化
7. 审计中产生的新知识先写入 `data/provisional/contests/<contest-slug>/`，不要直接污染正式 RAG；公开报告后确认有复盘价值的 Low/NC/QA 可少量归档到 `low_non_critical_cases` caution 通道
8. 等最终报告/提交结果确认后，先 dry-run `promote-provisional`，人工审校后再 `--confirmed` 归档到 `data/normalized/` 和正式 eval
9. 扩展更细的 component checklist / recipe；向量检索和重排模型仍然后置
10. 对 endpoint / message-library / Rust/Soroban 项目，参考 `docs/layerzero-stellar-postmortem-workflow.md`，HM 搜索结束后必须独立跑 QA/Low harvest

## 当前仓库里最重要的文档

### 总设计
- `docs/prd.md`
- `docs/retrieval-design.md`
- `docs/skill-aware-architecture.md`
- `docs/triage-interface.md`

### 学习辅助
- `docs/glossary-zh.md`
- `docs/smart-contract-audit-glossary-zh.md`

### 计划与执行
- `docs/week-1-plan.md`
- `docs/plans/2026-04-18-skill-aware-triage-implementation-plan.md`

## 当前仓库里最值得优先看的样本

### 原始机器可读版
- `data/normalized/case_reports/reward-debt-desync-case-01.json`
- `data/normalized/vulnerability_patterns/reward-debt-desync-pattern.json`
- `data/normalized/false_positive_cases/admin-bad-slippage-fp-01.json`
- `data/normalized/component_checklists/reward-distribution-checklist.json`
- `data/normalized/validation_recipes/reward-debt-desync-validation-recipe-01.json`

### 带中文注释版
- `data/normalized/case_reports/reward-debt-desync-case-01.annotated.jsonc`
- `data/normalized/vulnerability_patterns/reward-debt-desync-pattern.annotated.jsonc`
- `data/normalized/false_positive_cases/admin-bad-slippage-fp-01.annotated.jsonc`
- `data/normalized/component_checklists/reward-distribution-checklist.annotated.jsonc`
- `data/normalized/validation_recipes/reward-debt-desync-validation-recipe-01.annotated.jsonc`

## 当前代码里最关键的位置

- CLI 入口：`src/audit_rag/cli/main.py`
- lead ledger：`src/audit_rag/contest/lead_ledger.py`
- triage scorecard / suppression：`src/audit_rag/contest/scorecard.py`
- triage 逻辑：`src/audit_rag/retrieval/issue_triage.py`
- lexical-first 检索：`src/audit_rag/indexing/hybrid_search.py`
- skill runtime：`src/audit_rag/orchestration/skill_runtime.py`
- triage 契约：`src/audit_rag/contracts/triage.py`
- 基础模型：`src/audit_rag/domain/models.py`

## 如果你想让我直接继续最合理的下一步

你可以直接发：

```text
继续 audit-rag，去 /Users/qwe/Audit/audit-rag
先检查当前状态，再直接做最合理的下一步
```

我默认会理解为：
- 先看文档
- 再看样本和代码状态
- 然后优先补样本 / validate-data / triage 检索

## 一句话版本

如果你只想记一句话，就记这个：

```text
继续 audit-rag，路径 /Users/qwe/Audit/audit-rag，先检查状态再往下做
```
