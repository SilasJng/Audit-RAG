from __future__ import annotations

import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel, Field

from audit_rag.quality.data_quality import validate_normalized_data

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PROVISIONAL_DIR = _REPO_ROOT / "data" / "provisional" / "contests"
_NORMALIZED_DIR = _REPO_ROOT / "data" / "normalized"
_SCHEMA_DIR = _REPO_ROOT / "schemas"

LEAD_STATUSES = {
    "new",
    "investigating",
    "needs-poc",
    "poc-passed",
    "duplicate",
    "false-positive",
    "qa-low",
    "submission-ready",
    "suppressed",
    "abandoned",
}

PROMOTION_TARGETS = {
    "case_report": "case_reports",
    "vulnerability_pattern": "vulnerability_patterns",
    "component_checklist": "component_checklists",
    "validation_recipe": "validation_recipes",
    "false_positive_case": "false_positive_cases",
    "contest_note": "contest_notes",
}


class LeadRecord(BaseModel):
    id: str
    contest_slug: str
    title: str
    text: str
    status: str = "new"
    component: str | None = None
    files: list[str] = Field(default_factory=list)
    functions: list[str] = Field(default_factory=list)
    severity_guess: str = "unclear"
    current_blocker: str | None = None
    duplicate_check: str | None = None
    false_positive_risk: str | None = None
    validation_command: str | None = None
    poc_path: str | None = None
    related_rag_cases: list[str] = Field(default_factory=list)
    related_rag_patterns: list[str] = Field(default_factory=list)
    rag_triage_path: str | None = None
    final_decision: str | None = None
    created_at: str
    updated_at: str


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug[:80] or "lead"


def contest_dir(contest_slug: str) -> Path:
    return _PROVISIONAL_DIR / contest_slug


def ledger_path(contest_slug: str) -> Path:
    return contest_dir(contest_slug) / "lead-ledger.jsonl"


def rag_triage_dir(contest_slug: str) -> Path:
    return contest_dir(contest_slug) / "rag-triage"


def summary_path(contest_slug: str) -> Path:
    return contest_dir(contest_slug) / "contest-summary.md"


def load_leads(contest_slug: str) -> list[LeadRecord]:
    path = ledger_path(contest_slug)
    if not path.exists():
        return []
    leads: list[LeadRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        leads.append(LeadRecord.model_validate(json.loads(line)))
    return leads


def save_leads(contest_slug: str, leads: list[LeadRecord]) -> Path:
    path = ledger_path(contest_slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        json.dumps(lead.model_dump(), ensure_ascii=False, sort_keys=True) for lead in leads
    )
    if content:
        content += "\n"
    path.write_text(content, encoding="utf-8")
    return path


def _next_id(existing: list[LeadRecord], title: str) -> str:
    base = slugify(title)
    existing_ids = {lead.id for lead in existing}
    if base not in existing_ids:
        return base
    index = 2
    while f"{base}-{index}" in existing_ids:
        index += 1
    return f"{base}-{index}"


def add_lead(
    contest_slug: str,
    title: str,
    text: str | None = None,
    component: str | None = None,
    files: list[str] | None = None,
    functions: list[str] | None = None,
    severity_guess: str = "unclear",
    status: str = "new",
) -> dict[str, Any]:
    if status not in LEAD_STATUSES:
        raise ValueError(f"unsupported lead status: {status}")
    leads = load_leads(contest_slug)
    timestamp = now_iso()
    lead = LeadRecord(
        id=_next_id(leads, title),
        contest_slug=contest_slug,
        title=title,
        text=text or title,
        status=status,
        component=component,
        files=files or [],
        functions=functions or [],
        severity_guess=severity_guess,
        created_at=timestamp,
        updated_at=timestamp,
    )
    leads.append(lead)
    path = save_leads(contest_slug, leads)
    return {"status": "ok", "action": "add-lead", "ledger_path": str(path), "lead": lead.model_dump()}


def update_lead(contest_slug: str, lead_id: str, updates: dict[str, Any]) -> LeadRecord:
    leads = load_leads(contest_slug)
    for index, lead in enumerate(leads):
        if lead.id != lead_id:
            continue
        data = lead.model_dump()
        data.update({key: value for key, value in updates.items() if value is not None})
        if data.get("status") not in LEAD_STATUSES:
            raise ValueError(f"unsupported lead status: {data.get('status')}")
        data["updated_at"] = now_iso()
        updated = LeadRecord.model_validate(data)
        leads[index] = updated
        save_leads(contest_slug, leads)
        return updated
    raise KeyError(f"lead not found: {lead_id}")


def update_lead_record(contest_slug: str, lead_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    updated = update_lead(contest_slug, lead_id, updates)
    return {
        "status": "ok",
        "action": "update-lead",
        "ledger_path": str(ledger_path(contest_slug)),
        "lead": updated.model_dump(),
    }


def get_lead(contest_slug: str, lead_id: str) -> LeadRecord:
    for lead in load_leads(contest_slug):
        if lead.id == lead_id:
            return lead
    raise KeyError(f"lead not found: {lead_id}")


def list_leads(contest_slug: str, status: str | None = None) -> dict[str, Any]:
    leads = load_leads(contest_slug)
    if status:
        leads = [lead for lead in leads if lead.status == status]
    return {
        "status": "ok",
        "contest_slug": contest_slug,
        "ledger_path": str(ledger_path(contest_slug)),
        "count": len(leads),
        "leads": [lead.model_dump() for lead in leads],
    }


def save_triage_result(contest_slug: str, lead_id: str, result: dict[str, Any]) -> Path:
    directory = rag_triage_dir(contest_slug)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{lead_id}.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _lead_markdown_row(lead: LeadRecord) -> str:
    blocker = (lead.current_blocker or "").replace("\n", " ")[:120]
    return (
        f"| `{lead.id}` | {lead.status} | {lead.severity_guess} | "
        f"{lead.component or ''} | {lead.title} | {blocker} |"
    )


def export_contest_summary(contest_slug: str) -> dict[str, Any]:
    leads = load_leads(contest_slug)
    counts = Counter(lead.status for lead in leads)
    path = summary_path(contest_slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Contest Summary: {contest_slug}",
        "",
        f"Generated: {now_iso()}",
        "",
        "## Status counts",
        "",
    ]
    if counts:
        for status, count in sorted(counts.items()):
            lines.append(f"- `{status}`: {count}")
    else:
        lines.append("- no leads recorded")
    lines.extend(
        [
            "",
            "## Leads",
            "",
            "| id | status | severity | component | title | blocker / note |",
            "|---|---:|---:|---|---|---|",
        ]
    )
    lines.extend(_lead_markdown_row(lead) for lead in leads)
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- ledger: `{ledger_path(contest_slug)}`",
            f"- rag triage dir: `{rag_triage_dir(contest_slug)}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "status": "ok",
        "action": "export-contest-summary",
        "contest_slug": contest_slug,
        "summary_path": str(path),
        "lead_count": len(leads),
        "status_counts": dict(sorted(counts.items())),
    }



def _schema_for_record_type(record_type: str) -> Path | None:
    schema_names = {
        "case_report": "case_report.schema.json",
        "vulnerability_pattern": "vulnerability_pattern.schema.json",
        "component_checklist": "component_checklist.schema.json",
        "validation_recipe": "validation_recipe.schema.json",
        "false_positive_case": "false_positive_case.schema.json",
        "contest_note": "contest_note.schema.json",
    }
    name = schema_names.get(record_type)
    return _SCHEMA_DIR / name if name else None


def _schema_errors(record_type: str, candidate: dict[str, Any]) -> list[str]:
    schema_path = _schema_for_record_type(record_type)
    if not schema_path or not schema_path.exists():
        return [f"missing schema for record_type={record_type}"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(candidate)]

def _candidate_id(candidate: dict[str, Any], record_type: str) -> str:
    for key in ("id", "pattern_id", "recipe_id", "checklist_id"):
        value = candidate.get(key)
        if value:
            return str(value)
    return slugify(candidate.get("title") or candidate.get("name") or record_type)


def _iter_promotable_files(contest_slug: str) -> list[Path]:
    base = contest_dir(contest_slug)
    if not base.exists():
        return []
    return sorted(
        path
        for path in base.rglob("*.provisional.json")
        if path.is_file() and "rag-triage" not in path.parts
    )


def promote_provisional(contest_slug: str, confirmed: bool = False) -> dict[str, Any]:
    """Promote curated provisional candidate records into normalized data.

    This intentionally requires confirmed=True. Active-audit data must not be promoted
    accidentally; the caller should only set confirmed after final report/submission outcome
    and manual curation review.
    """

    planned: list[dict[str, Any]] = []
    promoted: list[dict[str, Any]] = []
    for source_path in _iter_promotable_files(contest_slug):
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        record_type = payload.get("candidate_record_type")
        candidate = payload.get("candidate")
        if record_type not in PROMOTION_TARGETS or not isinstance(candidate, dict):
            planned.append(
                {
                    "source": str(source_path),
                    "status": "skipped",
                    "reason": "missing or unsupported candidate_record_type/candidate",
                }
            )
            continue
        record_id = _candidate_id(candidate, record_type)
        target = _NORMALIZED_DIR / PROMOTION_TARGETS[record_type] / f"{record_id}.json"
        schema_errors = _schema_errors(record_type, candidate)
        item = {
            "source": str(source_path),
            "target": str(target),
            "record_type": record_type,
            "record_id": record_id,
            "schema_status": "ok" if not schema_errors else "failed",
            "schema_errors": schema_errors,
        }
        planned.append(item)
        if schema_errors:
            continue
        if confirmed:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(candidate, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            promoted.append(item)
    manifest = contest_dir(contest_slug) / "promotion-manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    validation_result = validate_normalized_data() if confirmed else None
    result = {
        "status": "ok" if not confirmed or validation_result["status"] == "ok" else "failed",
        "action": "promote-provisional",
        "confirmed": confirmed,
        "contest_slug": contest_slug,
        "planned_count": len(planned),
        "promoted_count": len(promoted),
        "planned": planned,
        "promoted": promoted,
        "validation_result": validation_result,
        "manifest_path": str(manifest),
        "warning": "confirmed=false is a dry run; use only after final outcome and curation review; add eval queries for every promoted retrieval family",
    }
    manifest.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return result


def mirror_to_contest_repo(contest_slug: str, contest_repo: str | Path) -> dict[str, Any]:
    """Copy the audit-rag ledger/triage summary into an active contest repo audit-context.

    The canonical state remains under audit-rag data/provisional; this mirror only makes it
    easy to inspect from the contest workspace.
    """

    source = contest_dir(contest_slug)
    target = Path(contest_repo) / "audit-context" / contest_slug / "audit-rag"
    if not source.exists():
        raise FileNotFoundError(f"contest provisional directory not found: {source}")
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    return {
        "status": "ok",
        "action": "mirror-to-contest-repo",
        "source": str(source),
        "target": str(target),
    }
