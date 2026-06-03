# LayerZero Stellar Endpoint 复盘后的审计流程改进

来源：Code4rena 2026-04 LayerZero Stellar Endpoint 公开报告复盘。

## 核心教训

这场比赛最终公开报告是 0 High / 0 Medium，但包含 Low、Non-critical、Informational 和大量 QA。我们本地当时的主要问题不是没有能力看代码，而是流程目标过窄：后期一直围绕“还能不能补出 submission-ready Medium/High”，没有把“独立 QA/Low harvest”作为必须阶段，也没有把 weak lead / downgrade lead 系统写入 audit-rag。

## 新默认流程

### 1. Intake 阶段

必须建立三类对象：

1. contest context
   - scope、commit、运行时、测试命令、known issues、公开报告/过往比赛链接。
2. component map
   - endpoint、message library、worker/DVN、treasury、codec、admin/config、storage TTL 等模块。
3. first-pass checklist
   - HM 搜索 checklist 和 QA/Low harvest checklist 分开记录。

### 2. HM search 阶段

目标只允许是 submission-ready Medium/High：

- 必须证明 permissionless 或 sponsor-accepted trusted role 下的真实影响。
- 必须有当前仓库可执行验证路线或 PoC。
- 必须跑 duplicate / known issue / public-known suppression。
- 如果 impact 依赖外部集成假设，默认降级，除非协议文档或代码明确承诺该 invariant。

### 3. Weak lead 记录阶段

非 trivial 线索即使不提交，也要写入 lead ledger：

```bash
python -m audit_rag.cli.main add-lead <contest-slug> \
  "short lead title" \
  --component <component> \
  --severity-guess qa-low \
  --status investigating \
  --text "why it looked suspicious + current blocker"
```

状态建议：

- `new`：刚发现，未分类。
- `investigating`：正在补证据。
- `needs-poc`：需要 PoC 或可执行复现。
- `qa-low`：确认偏 QA/Low，但仍有报告/复盘价值。
- `false-positive`：误报。
- `suppressed`：duplicate、known issue、out-of-scope、public-known 或 impact 不成立。
- `submission-ready`：可提交 HM。

### 4. 独立 QA/Low harvest 阶段

HM 搜索结束后必须另开一轮，不允许被“没有新 HM”替代。

Rust/Soroban endpoint-style repo 固定扫项：

- raw balance / donation / dust / refund / recover_token
- blocked/default message library 的 interface/capability mismatch
- persistent key TTL / rent / archive
- sentinel value，例如 NIL payload hash、zero amount、nonce 0
- Address account vs contract variant、tagless codec、round-trip serialization
- default config inheritance、custom/default library cutover、grace window
- quote/get_fee vs assign_job/payment amount consistency
- Worker/DVN/admin/signer Vec：duplicate、empty、unbounded、rotation、batch setter、signature high-s/v
- pagination u32、i128 sum/mul、unchecked casts

每条 QA/Low lead 也要记录 blocker：为什么没有升级到 Medium/High。

### 5. audit-rag 使用规则

- `triage-lead`：用于强 lead 或可能升级的 lead。
- `suppress-check`：用于 weak lead、疑似 duplicate、疑似 QA/Low、severity 不确定的 lead。
- `low_non_critical_cases`：保存有复盘价值的 Low/NC/QA 原始案例，进入 caution retrieval channel，不进入主 HM positive stream。
- `false_positive_cases`：保存“为什么这个 claim 不该按 HM 讲”的可复用降级判断。
- 审计结束后，先把本场 contest 的 weak lead 和 QA/Low harvest 结果导出 summary，再决定哪些记录能 promotion 到 normalized。

## 本次已反哺进 audit-rag 的记录

- `data/normalized/low_non_critical_cases/c4-2026-04-layerzero-stellar-endpoint-low-raw-balance-fee-donation.json`
- `data/normalized/low_non_critical_cases/c4-2026-04-layerzero-stellar-endpoint-low-blocked-message-lib-interface.json`
- `data/normalized/low_non_critical_cases/c4-2026-04-layerzero-stellar-endpoint-low-tagless-address-codec.json`
- `data/normalized/false_positive_cases/ambient-fee-balance-prefund-theft-overclaim-fp-01.json`
- `data/normalized/component_checklists/endpoint-message-library-low-harvest-checklist.json`

对应 eval：

- `eval-lz-stellar-raw-fee-balance-low`
- `eval-lz-stellar-blocked-message-lib-interface`
- `eval-lz-stellar-tagless-address-codec`

## 质量门槛

改流程或数据后必须跑：

```bash
cd /Users/qwe/Audit/audit-rag
source .venv/bin/activate
python -m audit_rag.cli.main validate-data
python -m audit_rag.cli.main --help
pytest -q
ruff check src tests scripts
```

如果只是改 skill，还要同步镜像：

```bash
python3.11 scripts/sync_skill_docs.py
```

## 失败条件

以下任一情况视为流程失败：

- 最终只留下 submission 文件，没有 weak lead / QA-low ledger。
- 复盘时无法区分“看过但误杀”和“根本没看”。
- Low/QA 线索直接混入 `case_reports` 主 HM 检索流。
- PoC 能跑但没有证明 sponsor/judge 会接受的 impact invariant。
- 公开报告后没有把有价值的 downgrade lesson 写入 `false_positive_cases` 或 `low_non_critical_cases`。
