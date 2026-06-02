from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DRAFT_ROOT = _REPO_ROOT / "data" / "provisional" / "ingestion-drafts"
_HEADING_RE = re.compile(r"^#{2,4}\s+\[(?P<severity>[HM])-?(?P<number>\d{1,2})\]\s*(?P<title>.+)$", re.MULTILINE)
_H2_RE = re.compile(r"<h2[^>]*>\s*\[(?P<severity>[HM])-?(?P<number>\d{1,2})\]\s*(?P<title>.*?)</h2>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")


def run_ingest(source_dir: str | Path) -> dict[str, Any]:
    """Create provisional finding drafts from raw report HTML/Markdown files.

    This is intentionally conservative: it never writes directly to data/normalized/.
    Drafts are meant for human curation before promote-provisional or manual normalized edits.
    """

    source_path = Path(source_dir)
    if not source_path.is_absolute():
        source_path = (_REPO_ROOT / source_path).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"source path not found: {source_path}")

    files = [source_path] if source_path.is_file() else sorted(source_path.glob("**/*"))
    supported = [path for path in files if path.suffix.lower() in {".html", ".htm", ".md", ".txt"}]
    drafts: list[dict[str, Any]] = []
    for path in supported:
        findings = _extract_findings(path)
        if not findings:
            continue
        out_dir = _DRAFT_ROOT / path.stem
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "draft-findings.json"
        payload = {
            "status": "draft",
            "source_path": str(path),
            "draft_count": len(findings),
            "findings": findings,
            "warning": "draft only; curate root_cause, invariants, snippets, validation_status, tags before normalized ingestion",
        }
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        drafts.append({"source_path": str(path), "draft_path": str(out_path), "count": len(findings)})

    return {
        "status": "ok",
        "action": "ingest-draft-reports",
        "source_path": str(source_path),
        "supported_files": len(supported),
        "draft_batches": drafts,
        "message": "created provisional drafts only; no normalized records were written",
    }


def _extract_findings(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in {".html", ".htm"}:
        return _extract_html_findings(text)
    return _extract_markdown_findings(text)


def _extract_markdown_findings(text: str) -> list[dict[str, Any]]:
    findings = []
    matches = list(_HEADING_RE.finditer(text))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        findings.append(_draft(match.group("severity"), match.group("number"), match.group("title"), section))
    return findings


def _extract_html_findings(text: str) -> list[dict[str, Any]]:
    findings = []
    matches = list(_H2_RE.finditer(text))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        section_html = text[start:end]
        section = html.unescape(_TAG_RE.sub(" ", section_html))
        section = re.sub(r"\s+", " ", section).strip()
        title = html.unescape(_TAG_RE.sub("", match.group("title"))).strip()
        findings.append(_draft(match.group("severity"), match.group("number"), title, section))
    return findings


def _draft(severity: str, number: str, title: str, section: str) -> dict[str, Any]:
    code = f"{severity.upper()}-{int(number):02d}"
    return {
        "finding_code": code,
        "severity": "high" if severity.upper() == "H" else "medium",
        "title": title.strip(),
        "section_excerpt": section[:3000],
        "curation_status": "needs-human-curation",
        "candidate_record_type": "case_report",
    }
