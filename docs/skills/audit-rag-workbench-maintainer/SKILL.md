---
name: audit-rag-workbench-maintainer
description: Maintain and extend the local audit-rag workbench at /Users/qwe/Audit/audit-rag — the stateful backend for smart-contract audit leads, triage evidence, suppression checks, PoC recipes, and provisional-to-normalized knowledge.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [python, rag, smart-contract-audit, audit-workbench, documentation]
---

# Audit RAG Workbench Maintainer

Use this skill when maintaining or extending the user's local project `/Users/qwe/Audit/audit-rag`. This is the implementation/maintenance skill for the audit-rag workbench itself, not the live C4 contest-audit workflow skill.

## Why this skill exists

This project is not a generic chatbot and no longer treats chat-style RAG as the product. It is a local, contest-oriented smart-contract audit workbench where audit-rag acts as the stateful backend for the contract-audit skill. The user prefers:
- Python over Go for this project
- Chinese-facing documentation
- terminal-friendly structure and outputs
- a workflow-aware design where skill defines stages/quality gates, audit-rag stores lead state and evidence, RAG provides knowledge, and AI performs reasoning

## Boundary with c4-contest-auditor

Keep this skill separate from `c4-contest-auditor`:
- `c4-contest-auditor` is the live contest-audit director: C4 intake, scope, known findings, severity guardrails, validation discipline, and submission packaging.
- `audit-rag-workbench-maintainer` is the backend maintainer: audit-rag repo structure, CLI/data/schema/test changes, skill-doc syncing, provisional/normalized policy, retrieval evals, and wiki/Obsidian integration boundaries.

Do not copy full C4 submission/reporting rules into this skill. Do not copy audit-rag implementation details into `c4-contest-auditor` beyond the thin active-audit calling contract.

## Environment findings

On this machine:
- `python3` resolves to `3.9.6`
- `python3.11` is available and should be used explicitly
- the project should target `>=3.11`

Do not assume `python3` is sufficient. Use `python3.11` for venv creation.

## When to use

- Maintaining the audit-rag repository, CLI, schemas, docs, tests, or data pipelines
- Extending lead-ledger, triage scorecard, suppress-check, promote-provisional, or runtime/category support
- Adding curated normalized data, provisional promotion rules, retrieval evals, or wiki/Obsidian boundaries
- Updating project docs under `docs/` and syncing related skill Markdown into the repo
- Verifying the local Python environment, test baseline, data validation, and ruff gate

## Required defaults

- Repo path: `/Users/qwe/Audit/audit-rag`
- Language: Python only
- Interface: CLI first
- Docs: Chinese for user-facing project docs
- Machine-readable config/schema keys: keep English
- First-stage architecture: `lead-ledger` + `candidate-triage` + `suppression-check`
- RAG is a knowledge recall layer; the project itself is the audit workbench/state backend

## Recommended repository structure

Keep or extend these key directories:
- `configs/`
- `data/raw/`
- `data/normalized/`
- `data/chunks/`
- `data/indexes/`
- `data/eval/`
- `docs/`
- `schemas/`
- `src/audit_rag/`
- `src/audit_rag/orchestration/`
- `src/audit_rag/contracts/`
- `tests/`

## Maintenance steps

### 1. Inspect before writing

Check whether `/Users/qwe/Audit/audit-rag` exists and what is already there.
Prefer `search_files` and `read_file` to inspect current files before editing.

### 2. Create or update the Python project skeleton when needed

Minimum top-level files:
- `README.md`
- `.gitignore`
- `.env.example`
- `pyproject.toml`

Minimum docs:
- `docs/prd.md`
- `docs/data-schema.md`
- `docs/tag-taxonomy.md`
- `docs/retrieval-design.md`
- `docs/local-setup.md`
- `docs/week-1-plan.md`
- `docs/glossary-zh.md`
- `docs/smart-contract-audit-glossary-zh.md`

If adding the workflow-aware architecture, also include:
- `docs/audit-workbench-direction.md`
- `docs/skill-aware-architecture.md`
- `docs/triage-interface.md`
- `docs/plans/<date>-skill-aware-triage-implementation-plan.md`

If adding the stateful audit backend, include:
- `src/audit_rag/contest/lead_ledger.py`
- `src/audit_rag/contest/scorecard.py`
- tests under `tests/contest/`

### 3. Use Chinese for human-facing docs

The user explicitly wanted the docs in Chinese.
Keep these Chinese:
- README explanatory sections
- PRD and planning docs
- glossary docs
- setup docs

Keep these English where appropriate:
- JSON schema keys
- Python identifiers
- config keys
- CLI/internal technical names such as `candidate-triage-v1`

### 4. Establish the first-stage architecture

The recommended design is:
- skill manages workflow and stage rules
- RAG provides pattern/case/false-positive/validation evidence
- AI reasons over current issue text and retrieved evidence

For the first implementation stage, focus on:
- `candidate-triage`

Add these code areas if absent:
- `src/audit_rag/orchestration/skill_runtime.py`
- `src/audit_rag/orchestration/stage_registry.py`
- `src/audit_rag/contracts/triage.py`
- `src/audit_rag/retrieval/query_context.py`

## Stateful audit workbench workflow

Current audit-rag direction:
- skill defines audit process, severity guardrails, C4 packaging, and when to call audit-rag
- audit-rag stores active lead state, triage evidence, suppression decisions, PoC recipes, and provisional/normalized knowledge
- RAG provides historical cases/patterns/false-positive/recipe evidence
- AI reasons over skill rules, current code evidence, and audit-rag evidence

Core CLI commands:
```bash
python -m audit_rag.cli.main add-lead <contest-slug> <title> [--text ...] [--component ...]
python -m audit_rag.cli.main list-leads <contest-slug>
python -m audit_rag.cli.main update-lead <contest-slug> <lead-id> [--status ...] [--current-blocker ...]
python -m audit_rag.cli.main triage-lead <contest-slug> <lead-id>
python -m audit_rag.cli.main suppress-check <contest-slug> <lead-id>
python -m audit_rag.cli.main export-contest-summary <contest-slug>
python -m audit_rag.cli.main promote-provisional <contest-slug> [--confirmed]
python -m audit_rag.cli.main mirror-contest-state <contest-slug> <contest-repo>
```

Default active-audit files:
- `data/provisional/contests/<contest-slug>/lead-ledger.jsonl`
- `data/provisional/contests/<contest-slug>/rag-triage/<lead-id>.json`
- `data/provisional/contests/<contest-slug>/contest-summary.md`
- `data/provisional/contests/<contest-slug>/promotion-manifest.json`

Rules:
1. Non-trivial active-audit leads must be recorded with `add-lead` before deep work.
2. Strong leads use `triage-lead`; weak/duplicate/QA-prone leads use `suppress-check`.
3. After PoC, duplicate review, or final decision, update the ledger with `update-lead`.
4. Cross-session continuation should use `export-contest-summary`.
5. `promote-provisional` is dry-run by default; only use `--confirmed` after final outcome and manual curation review.

Active-contest state sync discipline:
- Before committing provisional contest updates, run `export-contest-summary <contest-slug>` and `validate-data` from the audit-rag venv.
- Inspect `git status --short` and add only the intended contest files under `data/provisional/contests/<contest-slug>/`; do not sweep unrelated untracked contest directories into the commit.
- Commit audit-rag state in `/Users/qwe/Audit/audit-rag` separately from the active contest repo. Do not commit active contest repo changes unless the user explicitly asks.
- If `git push` prints a GitHub "repository moved" notice but exits `0`, treat the push as successful and mention the old/new remote mismatch; optionally update `origin` later, but do not report the push as failed.

## Minimal code expectations

### Triage output should include
- `query_type`
- `skill_name`
- `stage_name`
- `false_positive_risks`
- `submission_blockers`
- `sources`

### Retrieval should become context-aware

Do not leave retrieval permanently as `query: str` only.
Prefer evolving to:
- query text
- `QueryContext`

Recommended context fields:
- `skill_name`
- `stage_name`
- `component_type`
- `audit_goal`
- `require_false_positive_check`
- `desired_output_schema`

## Skill boundary / mirror maintenance workflow

Use this when renaming or refactoring local Hermes skills that are mirrored into `/Users/qwe/Audit/audit-rag/docs/skills/`, especially when separating a live audit adapter skill from the audit-rag backend maintainer skill.

Recommended steps:
1. Inspect local skill dirs under `~/.hermes/skills/software-development/` and the repo mirror under `docs/skills/` before editing.
2. For a local skill rename, move the directory and update SKILL.md frontmatter `name`, `description`, title, trigger text, and any self-references.
3. Keep boundary text explicit:
   - live contest skills such as `c4-contest-auditor` should keep only the thin active-audit calling contract for audit-rag
   - `audit-rag-workbench-maintainer` should keep repo/CLI/schema/data/test/sync implementation details
4. Update `/Users/qwe/Audit/audit-rag/scripts/sync_skill_docs.py` to point at the new local skill path and mirror directory.
5. Remove stale mirrored directories such as an old skill name under `docs/skills/` before running the sync script.
6. Run:
   ```bash
   cd /Users/qwe/Audit/audit-rag
   python3.11 scripts/sync_skill_docs.py
   ```
7. Search for stale old skill names in the repo and local skill content before committing.
8. Verify the audit-rag repo even if only docs/skills changed:
   ```bash
   source .venv/bin/activate
   python -m audit_rag.cli.main validate-data
   pytest -q
   ruff check .
   ```
9. Commit and push the mirror/script changes. If the rename changes future routing, update memory with the new local skill name.

## Local verification steps

From repo root:

```bash
cd /Users/qwe/Audit/audit-rag
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
python -m audit_rag.cli.main --help
pytest -q
```

Expected:
- CLI help prints successfully
- tests pass

## Practical lessons learned

1. Do not use `python3` for this repo bootstrap on this machine; it points to 3.9.6.
2. The user values Chinese docs enough that leaving key docs in English causes friction.
3. It is worth introducing the `skill-aware triage` architecture early, even before real retrieval is implemented, so the contract and stage model stabilize before deeper feature work.
4. Keep machine-readable schemas/configs in English even when prose docs are Chinese.
5. After changing docs or architecture skeleton, always rerun:
   - `python -m audit_rag.cli.main --help`
   - `pytest -q`

## First sample-data workflow

When the user asks how to start writing sample data, do not begin with automated extraction.
Start with a small hand-written, tightly scoped seed set under `data/normalized/`.

Recommended first batch:
- `case_reports/reward-debt-desync-case-01.json`
- `vulnerability_patterns/reward-debt-desync-pattern.json`
- `false_positive_cases/admin-bad-slippage-fp-01.json`
- `component_checklists/reward-distribution-checklist.json`
- `validation_recipes/reward-debt-desync-validation-recipe-01.json`

Why this batch works well:
- the records are cross-linked around one core bug family
- it demonstrates the difference between concrete case, abstract pattern, checklist, false-positive, and validation recipe
- it is enough to exercise the future `candidate-triage` flow without needing a large corpus

## Annotated sample-data workflow

The user found all-English JSON hard to follow.
When providing reference samples for learning, keep the machine-readable `.json` files intact, and generate parallel annotated teaching copies as `.annotated.jsonc` files.

Pattern:
- canonical machine-readable file: `*.json`
- human-readable teaching copy: `*.annotated.jsonc`

The `.annotated.jsonc` version should include:
- field-by-field Chinese explanations
- translations of important English values
- short notes on why a field matters in retrieval / triage

Do not add comments directly to the canonical `.json` files, because that breaks strict JSON consumers.

## Code4rena report ingestion workflow

When the user asks to “read this report and write it into audit-rag”, treat it as a data-ingestion task, not a generic summary task.

Recommended steps:
1. Save the original report under `data/raw/` using a stable slug, for example:
   - `data/raw/2025-04-kinetiq-report.html`
   - `data/raw/2025-04-kinetiq-report.md`
2. Fetch the HTML with `python3.11` and a browser-like User-Agent. Code4rena report pages are static enough to parse from HTML.
3. If BeautifulSoup is not installed, do not stop to add dependencies unless needed. A lightweight stdlib parser is often enough:
   - remove `<script>`, `<style>`, `<svg>` blocks
   - convert `h1/h2/h3/h4`, `p`, `li`, `pre`, and `code` tags into markdown-like text
   - unescape HTML entities
4. Extract High/Medium findings from headings matching:
   - `## [H-01] ...`
   - `## [M-01] ...`
5. Normalize High/Medium findings into `data/normalized/case_reports/` using IDs like:
   - `c4-YYYY-MM-protocol-h-01.json`
   - `c4-YYYY-MM-protocol-m-01.json`
6. Preserve report-provided GitHub blob permalinks in `snippets[].code`. These are valuable retrieval evidence and align with the user’s audit-report preference for fixed commit + line range links.
7. Extract Low/Non-critical sections into `data/normalized/low_non_critical_cases/` using IDs like:
   - `c4-YYYY-MM-protocol-low-01.json`
   Put these in `retrieval_channel: low_non_critical_caution` so they can support downgrade/false-positive reasoning without polluting the main High/Medium candidate stream.
8. Validate every new JSON file against the matching schema:
   - `schemas/case_report.schema.json`
   - `schemas/low_non_critical_case.schema.json`
9. Then run the local baseline:
   - `source .venv/bin/activate`
   - `python -m audit_rag.cli.main --help`
   - `pytest -q`

Practical extraction notes:
- Code4rena report HTML may be one very long line, so line-oriented grep can look odd; write an intermediate markdown/plaintext file before extracting headings.
- Some reports list a count of low/non-critical submissions, but the highlighted QA report may contain fewer numbered sections. Do not blindly keep all numbered QA items as retrieval knowledge.
- `validation_status` should reflect sponsor text when visible: `confirmed-by-sponsor`, `acknowledged-by-sponsor`, or `disputed-by-sponsor-but-included-in-final-report`.
- Do not let sponsor/judge/warden discussion leak into `mitigations`. When extracting `### Recommended Mitigation Steps`, stop at the next finding heading or before lines like `Sponsor ... confirmed/disputed/commented`, `judge commented`, or `warden commented`; keep only the concrete fix.
- Newer Code4rena reports may render affected code as `File: X.sol` plus numbered lines inside `<pre>` blocks instead of plain markdown links. Preserve those as fallback snippets like `X.sol#L208-L209`, but also parse the original HTML section for `href="https://github.com/.../blob/<commit>/...#L..."` links and prepend fixed GitHub blob permalinks when available.
- For reports using GitHub issue links instead of C4 submission links, preserve finding issue URLs in `snippets` with role `finding-reference`, while keeping actual code links as role `affected-code`.
- `root_cause` must be an abstract, reusable cause, not the first paragraph copied from the report. Never keep autogenerated prefixes like `Report-described logic/accounting flaw:`.
- `broken_invariants` must be issue-specific and retrieval-useful. Never keep generic templates like `The staking flow should preserve protocol accounting, authorization, and user fund invariants.`
- `tags` are semantic cross-protocol filters. Remove protocol names and severity/classification words such as `ethena`, `kinetiq`, `nudgexyz`, `high`, `medium`, `low`.
- Low/Non-critical/QA items should usually become `false_positive_cases` or be dropped. Keep only items that explain why a suspicious pattern is not Medium/High unless extra reachability/value-loss conditions are proven.
- Exception after the LayerZero Stellar Endpoint postmortem: keep a small number of reusable Low/NC/QA raw lessons in `data/normalized/low_non_critical_cases/` when they improve future suppression/checklist behavior (for example raw balance fee donation, message-library interface mismatch, tagless Soroban address codecs). These must stay in the caution channel, never in `case_reports` / positive HM retrieval.
- When adding `low_non_critical_cases`, update lexical retrieval so they are returned with `false_positive_cases` as caution evidence, add eval queries that expect them in `expected_caution_ids`, and document `why_not_medium_or_high` plus `when_it_could_escalate`.
- For the local project, keep the data quality policy in `docs/data-curation-quality-gate.md` and update it when the ingestion rules change.
- After ingestion or curation, if the project is already bound to GitHub, commit and push the changed raw + normalized + docs files after schema/test verification.
- For this project path, check git state first; do not assume commit or branch operations are available.

## Code4rena audit-page and mitigation-review workflow

When the user provides `https://code4rena.com/audits/...` URLs instead of `/reports/...`, do discovery first:

1. Fetch and save each audit page under `data/raw/<audit-slug>.html` and `data/raw/<audit-slug>.md`.
2. Search the audit page HTML for linked final reports such as `/reports/YYYY-MM-protocol`. Invitational audit pages often link the actual findings report; mitigation review pages often do not.
3. If a final `/reports/...` page exists, ingest that as the canonical source for High/Medium `case_reports`.
4. Save every provided audit page as a `contest_note` under `data/normalized/contest_notes/` with:
   - `id: c4-<audit-slug>`
   - `contest_name`
   - `repo_url`
   - `source_url`
   - `known_issues` containing linked GitHub finding issues where available
   - `architecture_summary` explaining that this is audit/mitigation context, not necessarily a final finding report
5. For mitigation-review audit pages:
   - Use GitHub findings repos linked from the page, e.g. `code-423n4/<contest>-mitigation-findings`.
   - Do not blindly convert all mitigation review issues into HM cases.
   - Only create a `case_report` when the issue body has enough evidence, direct affected code links, and a clear unresolved/unmitigated impact.
   - Use `validation_status: unmitigated-in-mitigation-review` for unmitigated review findings.
   - Use `false_positive_cases` for downgrade/context lessons such as “no-code/documentation mitigation may be acceptable if deployment assumptions bound the risk.”
6. For Code4rena GitHub issue APIs, `https://api.github.com/repos/<owner>/<repo>/issues/<number>` is enough for public repos; preserve the issue `html_url` as a finding-reference snippet.
7. Keep the same quality gates as report ingestion: abstract `root_cause`, issue-specific `broken_invariants`, semantic tags only, and schema/test/eval verification before commit.
8. If a command is blocked/denied by the user or security layer, do not retry that exact command. Continue with already validated data or use a safer narrower operation.

Practical example: Reserve Protocol 2023-07 audit page linked `/reports/2023-07-reserve`, which yielded 3 High + 15 Medium final findings. The 2023-08 and 2023-09 mitigation review pages were better stored as `contest_notes`; only one clearly unmitigated reward-rounding issue was promoted to `case_report`, and one no-code mitigation context was stored as `false_positive_case`.

## Lexical-first triage retrieval workflow

When external review says the project is still a stub, verify against the live repo first. In this project the minimal P0 retrieval path should be:

1. Add failing tests before implementation:
   - `tests/retrieval/test_hybrid_search.py` should assert `hybrid_search()` returns `status: ok`, ranked `positive_matches`, and separate `caution_matches`.
   - `tests/retrieval/test_issue_triage.py` should assert `triage_issue()` uses real retrieval sources, not `local://...placeholder`.
2. Implement `src/audit_rag/indexing/hybrid_search.py` as lexical-first before embeddings:
   - load local JSON records from `data/normalized/case_reports`, `vulnerability_patterns`, `validation_recipes`, and `false_positive_cases`
   - weight structured fields: `root_cause`, `finding_title`/`issue_claim`, `broken_invariants`, `tags`, `component_types`, `summary`
   - keep positive evidence separate from caution evidence: `positive_matches` vs `caution_matches`
   - include `score`, `matched_terms`, `document_type`, `source`, `source_url`, and key fields needed by triage
   - use `QueryContext.component_type` and `stage_name` only as lightweight boosts, not as hard filters
3. Update `triage_issue()` to consume retrieval results:
   - top case fills `likely_root_cause`, `broken_invariant`, `probable_severity_range`, `matching_cases`, `sources`
   - caution matches fill `false_positive_risks`
   - always keep a blocker saying historical similarity is not proof; current code reachability/impact still need validation
4. Add a tiny eval set under `data/eval/retrieval_queries.jsonl` with `expected_positive_ids` and `expected_caution_ids`.
5. Verify:
   - `python -m audit_rag.cli.main validate-data`
   - `pytest -q`
   - run the eval JSONL manually or via a future eval command
   - `python -m audit_rag.cli.main --help`
6. Update docs after behavior changes:
   - README current status
   - `docs/data-schema.md` if Low/QA handling changes
   - `docs/continue-here.md` to avoid stale “检索骨架/TODO” wording
   - `docs/data-curation-quality-gate.md` when adding or tightening data quality gates
7. If the repo is bound to GitHub, commit and push after tests and eval pass.

Practical lessons:
- Do not preserve `hybrid_search` as a TODO once there are normalized samples. A simple lexical-first retriever is more valuable than a planned but absent embedding pipeline.
- Batch-ingested case reports often pass schema while still having weak retrieval value. Add regression tests and a CLI gate for semantic data quality, not just JSON shape.
- The project now has `src/audit_rag/quality/data_quality.py` and `python -m audit_rag.cli.main validate-data`; use it after every ingestion/curation batch.
- Treat these root-cause prefixes as failures because they indicate autogenerated or title-copy text: `Report-described`, `protocol invariant violation in`, `state/accounting validation gap in`.
- Treat `condition described by` inside `broken_invariants` as a failure; replace it with root-cause-specific invariants tied to valuation, liquidation, withdrawal, rewards, authorization, DoS, reentrancy, or numeric-domain safety.
- When data volume passes ~100 JSON records, cache local JSON loading in lexical retrieval, but keep the cache process-local and simple until a real index exists.

## Pattern/checklist/recipe expansion workflow

When the user asks to continue filling audit-rag from existing confirmed cases or public final reports, treat it as curation plus retrieval-regression work, not just JSON generation.

Important boundary:
- During an active audit, do not add newly discovered candidate cases, patterns, recipes, false-positive judgments, or eval queries directly to `data/normalized/` or formal `data/eval/retrieval_queries.jsonl`.
- Store active-audit knowledge under `data/provisional/contests/<contest-slug>/` first.
- Promote from provisional to normalized only after the final report/submission outcome is confirmed and the record has been re-curated for root cause, broken invariant, impact, and downgrade risk.

Recommended steps:
1. Inspect current repo state first:
   - `git status --short`
   - count JSON records under `data/normalized/case_reports`, `false_positive_cases`, `vulnerability_patterns`, `component_checklists`, `validation_recipes`, and `contest_notes`
   - read the schemas before generating new normalized objects
2. Derive `vulnerability_patterns` from existing strong case reports when possible, and set `related_case_ids` to real local case ids. Avoid orphaned abstract patterns with no traceable evidence.
3. Keep generated patterns/checklists/recipes schema-small and retrieval-useful:
   - patterns: reusable `description`, concrete `broken_invariants`, `common_triggers`, `preconditions`, `typical_impact`, `common_false_positives`, `validation_methods`
   - checklists: component-level `core_invariants`, `trust_boundaries`, `common_bug_classes`, `check_items`, `test_ideas`, `related_pattern_ids`
   - recipes: actionable `goal`, `setup_requirements`, `minimal_state`, `attacker_actions`, `assertions`, `common_failures`
4. Extend `hybrid_search.py` when adding new document classes to retrieval. For component checklists, add:
   - `component_checklist` to `DOCUMENT_SETS`
   - field weights for `component_type`, `core_invariants`, `trust_boundaries`, `common_bug_classes`, `check_items`, `test_ideas`, `related_pattern_ids`
   - projection output with `core_invariants`, `check_items`, and `common_bug_classes`
   - include `component_checklist` in the positive retrieval channel while keeping `false_positive_case` separate
5. Expand `data/eval/retrieval_queries.jsonl` with one or more expected ids for every new retrieval family:
   - case report queries
   - false-positive/caution queries
   - pattern-level queries
   - checklist-level queries
6. Add or maintain a pytest regression such as `tests/retrieval/test_eval_queries.py` that reads the JSONL and asserts all `expected_positive_ids` and `expected_caution_ids` are returned by `hybrid_search()`.
7. Verification gate before commit:
   - `source .venv/bin/activate`
   - `python -m audit_rag.cli.main validate-data`
   - `python -m audit_rag.cli.main --help`
   - `pytest -q`
   - optionally run a manual eval script that prints missing expected ids before debugging
8. Update README counts and retrieval coverage wording after data expansion.
9. Commit and push only after validation, tests, eval, and README are synchronized.

Practical lessons:
- `validate-data` can pass while retrieval coverage is still weak; always pair curation with eval queries.
- Expanding data object types may require retriever field weights and projection changes, otherwise new records exist but are not useful to RAG.
- When adding or newly relying on `validation_recipes`, ensure `src/audit_rag/indexing/hybrid_search.py` weights recipe fields such as `goal`, `setup_requirements`, `minimal_state`, `attacker_actions`, `assertions`, `common_failures`, and `notes`; otherwise recipe evals may fail even though schema validation passes.
- Keep eval expectations stable and specific: for a query derived from one newly curated case, require the exact case id; only add broad checklist/pattern ids to `expected_positive_ids` when the current retriever actually and consistently ranks them. Use a recipe-specific query when expecting a validation recipe in top matches.
- If eval output is truncated, rerun a narrower script that prints only missing ids and top retrieved ids.
- When README says old counts such as 1 pattern / 1 checklist / 1 recipe, update it in the same commit as the data expansion to avoid stale continuation context.
- Monetrix M-01 net-equity curation details and retrieval-regression pitfall are captured in `references/monetrix-net-equity-curation.md`.
- Repo maintenance optimization notes from the post-Monetrix review are captured in `references/audit-rag-maintenance-optimization-review.md`: focused lint scope, CI baseline, ingest stub hardening, stronger quality gates, stricter evals, configurable field weights, wiki lint, and promote-provisional gates.
- Concrete implementation notes for those maintenance gates are captured in `references/maintenance-gates-implementation.md`, including safe ingest-draft behavior, wiki-lint count pitfalls, optional eval expectations, promote schema/quality gates, and the GitHub PAT `workflow` scope needed when committing `.github/workflows/*.yml`.

## Project maintenance optimization checklist

Use this checklist when the user asks “what else can be optimized” or after a successful audit-rag curation/push cycle:

1. Remote hygiene:
   - If GitHub reports a moved repository but push exits `0`, treat the push as successful, then update `origin` with `git remote set-url origin <new-url>` and verify with `git fetch origin --prune && git status -sb`.
2. Lint scope:
   - Do not let `ruff check .` lint third-party/raw report artifacts under `data/raw/**` or generated wiki/output directories.
   - Prefer `ruff check src tests scripts`, or add `pyproject.toml` excludes for raw/generated/vendor-like paths.
3. CI baseline:
   - Add/maintain GitHub Actions around Python 3.11, `validate-data`, `pytest -q`, and scoped ruff.
4. Stub commands:
   - Any exposed CLI command that still behaves as a TODO should either fail explicitly with guidance or produce safe draft/provisional output; avoid a command that appears to succeed while doing nothing.
5. Data quality:
   - Tighten `validate-data` beyond schema shape: source URLs, snippets/blob permalinks, id/filename consistency, validation-status vocabulary, and polluted tags.
6. Retrieval eval:
   - Pair each new retrieval family with eval. Add top-rank/type/runtime expectations when the current simple “id appears somewhere” check is too weak.
7. Promotion safety:
   - `promote-provisional --confirmed` should eventually validate candidate schema, run quality gates after write, and warn if eval coverage is missing.
8. Three-batch hardening reference:
   - See `references/audit-rag-three-batch-hardening.md` for the concrete implementation pattern covering ruff/CI, safe ingest drafts, semantic data-quality gates, stricter retrieval evals, promote-provisional schema/quality gates, configurable retrieval weights, wiki lint, and cleanup/verification discipline.

## External audit-report sweep workflow

When the user provides a set of public audit reports, GitHub audit directories, or PDF audit reports to enrich audit-rag for an active contest, treat it as an external-report sweep plus retrieval-regression task.

Recommended steps:
1. Save all raw sources under a stable batch directory such as `data/raw/external-reports-<contest-slug-or-date>/`.
2. For GitHub audit directories, use the GitHub contents API instead of scraping the web UI:
   - `https://api.github.com/repos/<owner>/<repo>/contents/<path>?ref=<branch>`
   - recursively walk directories, save `file-list.json`, then download each `download_url` or raw URL.
   - URL-quote file names containing spaces or Unicode punctuation.
3. For PDFs, load the generic `ocr-and-documents` skill. On this machine, do not install PDF libraries into the externally-managed `python3.11`; activate the audit-rag `.venv` first, then install/use `pymupdf` there if needed:
   - `cd /Users/qwe/Audit/audit-rag && source .venv/bin/activate && pip install pymupdf`
   - extract each PDF to adjacent `.txt` under the raw batch directory.
4. Extract only retrieval-useful lessons into normalized data:
   - confirmed HM-like findings become `case_reports`
   - reusable causes become `vulnerability_patterns`
   - contest-specific synthesis becomes `data/provisional/contests/<slug>/...md`
   - downgrade/theoretical/dust-only lessons become `false_positive_cases`
   - add at least one `component_checklist` or `validation_recipe` when the sweep is meant to guide an active contest.
5. For active contests, it is acceptable to add curated public historical cases to `data/normalized/`, but keep the contest-specific mapping and smoke leads under `data/provisional/contests/<contest-slug>/`.
6. Preserve strict-runtime hygiene: if a pattern is intended for Soroban/Rust retrieval, set `applicable_languages: ["rust-soroban"]` even when the original analogy came from Solidity; keep the cross-runtime source in `related_case_ids`/description. Otherwise strict Soroban queries may return Solidity metadata and fail runtime-regression tests.
7. Append eval queries for every new family: direct case, pattern/checklist, and caution channel.
8. Run the full gate before committing:
   - `source .venv/bin/activate`
   - `python -m audit_rag.cli.main validate-data`
   - `python -m audit_rag.cli.main --help`
   - `pytest -q`
   - create one temporary `add-lead` + `triage-lead` smoke test for the active contest and confirm it retrieves the new records.
9. Update README counts and retrieval coverage wording in the same commit as the data changes.
10. Commit and push after verification; if GitHub reports a moved repository, note the redirect/remote mismatch separately rather than treating push as failed.

Practical example: a K2 Stellar/Soroban lending sweep used Reflector V3 for native Soroban `require_auth`, TTL/vector, and oracle partial-update cases, and Silo v3 PDF audits for lending hook/callback, stale solvency config after debt transfer, and dynamic oracle calldata lessons. The K2-specific synthesis stayed under `data/provisional/contests/2026-04-k2/`, while curated historical records went into `data/normalized/` with eval queries and a `triage-lead` smoke test.

## New runtime/category expansion workflow

When the user asks to add a new audit category/runtime to audit-rag (for example moving beyond EVM/Solidity into Stellar/Soroban Rust, Move, Cosmos, or other ecosystems), treat it as a researched corpus-extension task, not just JSON generation.

Recommended steps:
1. Inspect the current repository state, schemas, counts, retrieval implementation, and git status before writing:
   - `git status --short`
   - count JSON files in `case_reports`, `vulnerability_patterns`, `component_checklists`, `validation_recipes`, `false_positive_cases`, and eval queries
   - read the relevant schemas and current `hybrid_search.py` behavior
2. Research both ecosystem-specific vulnerability guidance and public contest/final reports:
   - use public security checklists/docs/blogs for runtime-specific primitives
   - use Code4rena `/reports/...` pages or other final reports for confirmed High/Medium evidence
   - save raw report HTML and a markdown/plaintext extraction under `data/raw/`
3. For Code4rena report HTML, parse headings directly from `<h2 id="...">[H/M-..]` sections when the markdown extraction does not produce `## [H-..]` headings. Newer C4 pages can embed escaped HTML/JSON and duplicate table-of-contents text; extract actual finding sections, not only ToC matches.
4. Seed the new category with a balanced retrieval set:
   - several confirmed `case_reports` with fixed GitHub blob links in `snippets[]`
   - reusable `vulnerability_patterns` derived from real cases and public runtime guidance
   - one runtime-level `component_checklist`
   - practical `validation_recipes`
   - at least one `false_positive_case` that captures a common overclaim/downgrade trap
   - eval queries that require the new category records to be retrieved
5. Keep tags semantic and runtime-searchable, e.g. `soroban-rust`, `stellar-rust`, `require-auth`, `storage-ttl`, `integer-math`; do not use severity words or protocol names as tags.
6. For Stellar/Soroban Rust specifically, good first-class families are:
   - `Address.require_auth` missing, wrong subject, or alternate-entrypoint bypass
   - storage TTL/rent/unbounded storage DoS or state-loss risk
   - duplicate `Vec` reserve/asset inputs causing double counting or auction overpricing
   - reward/emission/interest index not updated before balance or config mutation
   - integer-only fixed-point math mistakes such as division-before-multiplication, zero denominators, and low-supply rounding
   - pool status/freeze checks bypassed through flash-loan or alternate operation paths
7. Pair the normalized additions with retrieval regression:
   - append `data/eval/retrieval_queries.jsonl` entries for case, pattern, checklist, and caution channels
   - create a temporary lead with `add-lead`, then manually run one `triage-lead` or `suppress-check` smoke test that should retrieve the new category
   - for long-term multi-chain support, add or verify strict runtime tests using `QueryContext(ecosystem=..., language=..., runtime=..., strict_runtime=True)` so EVM/Solidity queries exclude known Soroban records and Soroban queries exclude known Solidity records
8. When runtime-specific data grows, upgrade the retrieval context rather than creating separate RAGs:
   - `QueryContext` should include `ecosystem`, `language`, `runtime`, and `strict_runtime`
   - default soft runtime mode should boost matching runtime records while still allowing cross-ecosystem analogies
   - `--strict-runtime` should hard-filter records that do not match the requested runtime metadata; untagged/unknown records are excluded, so new data should carry explicit `language` / `applicable_languages` or runtime-searchable tags
   - CLI examples: `--ecosystem evm --language solidity --runtime evm` and `--ecosystem stellar --language rust-soroban --runtime soroban --strict-runtime`
9. Verification gate before commit:
   - `source .venv/bin/activate`
   - `python -m audit_rag.cli.main validate-data`
   - `python -m audit_rag.cli.main --help`
   - `pytest -q`
   - one temporary-ledger `triage-lead` / `suppress-check` smoke test for the new category
9. Update README counts and retrieval coverage wording, then commit and push if the repo is bound to GitHub.

Practical lessons from adding Stellar/Soroban Rust:
- Code4rena's Blend V2 report was a useful Stellar/Soroban Rust seed because it had many confirmed H/M findings and report-provided GitHub blob links.
- C4 report pages may contain many duplicate `[H-..]` / `[M-..]` strings from ToC and embedded page data. Use actual `<h2>` finding sections and section-local GitHub links to avoid wrong snippet attribution.
- For runtime-specific categories, include at least one false-positive/downgrade record early. Example: an internal helper missing `require_auth` is not a finding unless a public entrypoint reaches it without authenticating the same consumed account.
- Do not rely on `validate-data` alone; it proves schema shape, not retrieval usefulness. Eval queries plus a temporary-ledger `triage-lead` / `suppress-check` smoke test are required for category expansion.

## Obsidian / LLM Wiki evaluation and integration workflow

When the user asks whether to add Obsidian, an LLM Wiki, a markdown knowledge base, or a human-readable notes layer to `/Users/qwe/Audit/audit-rag`, treat it as an architecture fit assessment before implementation.

Session-specific POC reference: `references/obsidian-wiki-poc.md` captures the first working wiki shape, seed topic, boundary rules, and wikilink verification pattern.

Default conclusion from the current project state:
- Obsidian / LLM Wiki can improve later audits, but should be an upper reading/synthesis/navigation layer, not the authoritative retrieval engine.
- Keep `data/normalized/` JSON, schemas, eval queries, and CLI triage as the machine-readable source of truth.
- Use wiki/Obsidian for concepts, cross-case synthesis, false-positive/downgrade lessons, comparisons, and reusable query writeups.
- Do not replace `hybrid_search.py`, schema validation, or eval regression with markdown search.

Recommended fit check:
1. Inspect live repo first:
   - `git status --short`
   - count `case_reports`, `vulnerability_patterns`, `component_checklists`, `validation_recipes`, `false_positive_cases`, `contest_notes`, and eval lines
   - read README, retrieval design, and current retriever behavior
   - verify `validate-data`, CLI help, and `pytest -q` if proposing code changes
2. Check environment before claiming integration exists:
   - `WIKI_PATH`
   - `OBSIDIAN_VAULT_PATH`
   - whether default `~/wiki` or `~/Documents/Obsidian Vault` exists
3. Recommend a lightweight POC before broad rollout:
   - create `/Users/qwe/Audit/audit-rag/wiki/` only if the user wants to proceed
   - initialize `SCHEMA.md`, `index.md`, and `log.md`
   - choose one high-value vulnerability family first, such as async bridge accounting, reward debt desync, oracle freshness/price domain, or Soroban `require_auth`
   - if choosing Soroban `require_auth`, the proven seed shape is: one concept page, one false-positive/downgrade page, one triage-query page, and one generated source-map page linking `soroban-require-auth-entrypoint-bypass-pattern`, `c4-2025-02-blend-v2-h-02`, `c4-2025-02-blend-v2-m-01`, `soroban-internal-helper-missing-require-auth-fp-01`, and `soroban-require-auth-entrypoint-matrix-recipe`
   - write 3-5 substantive pages maximum; avoid broad auto-generation until the user confirms the reading workflow is useful
4. Preserve layer boundaries:
   - `wiki/generated/` may contain read-only markdown exported from `data/normalized/`; mark it generated and do not edit manually
   - `wiki/concepts/`, `wiki/comparisons/`, and `wiki/queries/` may contain agent/human synthesized pages
   - active audit knowledge still belongs under `data/provisional/contests/<slug>/` first; if mirrored to wiki, mark it provisional/low-confidence and do not promote it to `data/normalized/` or formal eval until confirmed
5. Current wiki integration:
   - `export-wiki` CLI exists and exports normalized JSON to read-only Markdown under `wiki/generated/`
   - first committed shape used Soroban `require_auth` concept/false-positive/query pages plus a generated index for 193 normalized records
6. Future integration can add:
   - `related_wiki_pages` in triage output as explanation/navigation, while JSON retrieval remains the evidence source
   - wiki lint for broken links, stale pages, unindexed pages, and low-confidence claims
   - optional filtering such as exporting only one bug family when full generated output is too noisy

Avoid:
- converting existing normalized JSON records into hand-maintained markdown as the primary source
- letting wiki pages automatically write back to `data/normalized/`
- bulk-generating hundreds of wiki pages without schema/index/log maintenance
- storing unconfirmed active-audit conclusions as formal concepts
- letting Obsidian/LLM Wiki become a second unsynchronized source of truth

Overlap note:
- Use the generic `llm-wiki` and `obsidian` skills for wiki mechanics.
- Use this `audit-rag-workbench-maintainer` section for audit-rag-specific boundaries, source-of-truth policy, and quality gates.
- See `references/obsidian-wiki-layer-assessment.md` for the condensed assessment of using an X/Twitter-style Obsidian local knowledge-base approach with audit-rag, including the recommended `wiki/` layout and first POC shape.

## Good next steps after maintenance changes

In priority order:
1. add first sample JSON records under `data/normalized/`
2. add parallel `.annotated.jsonc` teaching copies for the seed records
3. implement `validate-data` CLI command
4. replace placeholder `triage_issue()` logic with lexical-first sample retrieval
5. separate positive match and caution channels in real retrieval output

## Avoid

- switching the project to Go just for learning purposes
- storing workflow rules only in prose docs without matching code contracts
- turning triage into free-form chat output
- mixing false-positive results into the same main ranking stream as positive cases
- translating JSON field names or Python identifiers into Chinese
