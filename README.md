# audit-rag

一个面向竞赛型智能合约审计的本地线索台账、降级判断和 PoC recipe 工作台。RAG 是其中的知识召回层，不是项目本体。

## 项目定位

目标是服务 Code4rena、Sherlock 这类比赛型审计流程。项目不再追求“更像聊天式 RAG”，而是作为合约审计 skill 的状态化后端：skill 定义流程、质量门槛和提交规则；audit-rag 记录审计过程中的 lead、triage 证据、false-positive / duplicate 风险、PoC recipe 和可复用知识。

能帮助你：
- 让每次审计产生的线索不丢、不重复追
- 更快召回相关漏洞模式、组件 checklist、validation recipe 和降级风险
- 更快判断候选问题值不值得继续追，或应该 QA/Low / duplicate / false-positive suppression
- 为强 lead 生成可执行的验证路线和报告收窄建议
- 把活跃审计中的候选知识先放入 provisional，审计结束后再把确认过的新模式、false-positive 和 recipe 反哺回正式知识库

活跃审计中的未确认的线索不直接进入正式 RAG。先放在 `data/provisional/contests/<contest-slug>/`，等最终报告或提交结果确认后，再经过归档审校写入 `data/normalized/` 和正式 eval。

## 首版范围

当前版本采用：
- Python-first
- local-first
- CLI-first
- 线索台账和结构化知识库优先

首版重点：
- lead ledger：活跃审计线索生命周期管理
- lexical-first 检索 + 元数据/阶段上下文轻量加权
- 候选问题 triage scorecard
- false positive / duplicate / downgrade suppression
- PoC validation recipe 生成
- skill-aware triage 骨架

当前状态：
- `case_reports`: 117 条，主召回流只放 Medium/High 和少量手写高质量样本；已新增 Stellar/Soroban Rust 类目样本，以及 K2 借贷审计可复用的 Reflector V3、Wise Lending、Silo v3 hook / solvency / oracle 配置案例
- `false_positive_cases`: 23 条，用于降级、误报和 QA-like caution 通道
- `vulnerability_patterns`: 25 条，已从现有 C4 样本提炼出 oracle、connector、liquidation、access control、withdrawal、reward、cross-domain queue、Stellar/Soroban Rust、hook callback、stale solvency cache 等核心模式
- `component_checklists`: 10 条，用于组件级 intake / 模块审计辅助，包含 `stellar-soroban-rust-checklist` 和 `k2-soroban-lending-external-report-checklist`
- `validation_recipes`: 15 条，用于把候选问题转成 PoC / 单测 / 状态机验证路线
- `contest_notes`: 3 条，用于保存 audit page / mitigation review 上下文
- `hybrid_search.py`: 已有 lexical-first 实现；同时召回 case / pattern / validation recipe，并保持 false-positive caution 通道独立；支持 `ecosystem` / `language` / `runtime` 软加权和 `strict_runtime` 强过滤
- `lead-ledger`: 已新增活跃审计线索台账，默认落盘到 `data/provisional/contests/<contest-slug>/lead-ledger.jsonl`
- `triage-lead`: 已新增基于 RAG 的 lead scorecard，输出 root-cause/pattern 相似度、suppression signals、validation recipe 和 report framing，并保存到 `data/provisional/contests/<contest-slug>/rag-triage/`
- `suppress-check`: 已新增 duplicate / false-positive / QA downgrade 风险检查入口
- `update-lead`: 已新增 PoC、duplicate review、最终判断后的 lead 状态更新入口
- `export-contest-summary`: 已新增 contest lead 总结导出，默认写入 `data/provisional/contests/<contest-slug>/contest-summary.md`
- `promote-provisional`: 已新增 provisional→normalized 的安全归档入口，默认 dry-run，必须显式 `--confirmed` 才会写入正式 normalized
- `export-wiki`: 已新增 Obsidian/Markdown 人读知识层导出，默认把 `data/normalized/` 只读导出到 `wiki/generated/`
- `docs/skills/`: 已镜像相关 Hermes skill Markdown；后续 skill 更新后运行 `python3.11 scripts/sync_skill_docs.py` 同步进仓库
- `data/eval/retrieval_queries.jsonl`: 41 条手工 recall 查询样本，已覆盖 case / false-positive / pattern / checklist，并纳入 `pytest` 回归测试
- `data/provisional/`: 活跃审计中的候选知识和 lead 状态暂存区，不参与正式 RAG 检索；最终确认后再归档

当前架构默认采用：
- skill 定义阶段、质量门槛、默认输入输出契约
- audit-rag 作为 skill 的状态化后端，负责 lead ledger、triage 证据、suppression 判断和 PoC recipe
- RAG 提供 pattern / case / false-positive / validation 证据
- AI 在阶段上下文、当前代码证据和检索证据约束下组织结论

## 目录说明

- `configs/`：项目配置
- `data/`：原始数据、正式结构化数据、provisional 候选知识、chunk、索引、评测集
- `docs/`：PRD、schema、标签体系、检索设计、阶段架构、术语表、周计划
- `src/audit_rag/contest/`：lead ledger、triage scorecard、suppression check 等活跃审计状态化后端
- `src/audit_rag/orchestration/`：skill-aware 工作流运行时与阶段配置
- `src/audit_rag/contracts/`：阶段输入输出契约模型
- `schemas/`：核心知识对象的 JSON Schema
- `src/audit_rag/`：Python 源码
- `tests/`：测试目录

## 快速开始

```bash
cd /Users/qwe/Audit/audit-rag
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
python -m audit_rag.cli.main --help
python -m audit_rag.cli.main validate-data
pytest -q
```

活跃审计 lead ledger 示例：

```bash
# 记录一个候选线索；默认写入 data/provisional/contests/<slug>/lead-ledger.jsonl
python -m audit_rag.cli.main add-lead 2026-04-example \
  "Bridge accounting clears retry state before async settlement" \
  --component cross-domain-bridge \
  --text "CoreWriter emits async action but local retry accounting is cleared before destination funds arrive"

# 对已记录 lead 运行 RAG-backed scorecard，并把原始输出保存到 rag-triage/<lead-id>.json
python -m audit_rag.cli.main triage-lead 2026-04-example bridge-accounting-clears-retry-state-before-async-settlement

# PoC、duplicate review 或最终判断后更新 lead 状态
python -m audit_rag.cli.main update-lead 2026-04-example bridge-accounting-clears-retry-state-before-async-settlement \
  --status needs-poc \
  --current-blocker "need runnable current-repo PoC"

# 专门检查 duplicate / false-positive / QA downgrade 风险
python -m audit_rag.cli.main suppress-check 2026-04-example bridge-accounting-clears-retry-state-before-async-settlement

# 导出当前 contest lead 总结；默认写入 data/provisional/contests/<slug>/contest-summary.md
python -m audit_rag.cli.main export-contest-summary 2026-04-example

# 审计结束后先 dry-run promotion；确认最终结果和人工审校后才加 --confirmed
python -m audit_rag.cli.main promote-provisional 2026-04-example

# 导出 Obsidian/Markdown 人读知识层；generated 页是只读导航，不替代 normalized JSON
python -m audit_rag.cli.main export-wiki
```

多链/多运行时检索示例：

```bash
# 默认 soft runtime：允许跨生态相似案例参与召回，但会对匹配 runtime 的记录加权
python -m audit_rag.cli.main triage-issue "ERC4626 donation manipulates share price" --ecosystem evm --language solidity --runtime evm

# strict runtime：过滤掉已知冲突生态/语言/运行时的记录，适合只想看 Stellar/Soroban Rust 证据时使用
python -m audit_rag.cli.main triage-issue "Soroban duplicate reserve Vec overprices bad debt auction" --ecosystem stellar --language rust-soroban --runtime soroban --strict-runtime
```

## 建议先读的文档

1. `docs/prd.md`
2. `docs/data-schema.md`
3. `docs/tag-taxonomy.md`
4. `docs/retrieval-design.md`
5. `docs/skill-aware-architecture.md`
6. `docs/triage-interface.md`
7. `docs/glossary-zh.md`
8. `docs/smart-contract-audit-glossary-zh.md`
9. `docs/week-1-plan.md`
10. `docs/local-setup.md`

## 设计原则

1. 所有输出都要可追溯到来源。
2. 相似模式不等于漏洞已成立。
3. 严重性判断默认保守。
4. false-positive 抑制是核心能力，不是附属功能。
5. 优先优化真实审计流程里的可用性，而不是做演示型功能。
6. skill 管流程，RAG 管知识，AI 管推理。
