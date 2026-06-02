from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from audit_rag.retrieval.query_context import QueryContext

_REPO_ROOT = Path(__file__).resolve().parents[3]
_NORMALIZED_DIR = _REPO_ROOT / "data" / "normalized"
_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


DOCUMENT_SETS = {
    "case_report": _NORMALIZED_DIR / "case_reports",
    "vulnerability_pattern": _NORMALIZED_DIR / "vulnerability_patterns",
    "component_checklist": _NORMALIZED_DIR / "component_checklists",
    "validation_recipe": _NORMALIZED_DIR / "validation_recipes",
    "false_positive_case": _NORMALIZED_DIR / "false_positive_cases",
}


DEFAULT_FIELD_WEIGHTS = {
    "id": 1.0,
    "finding_title": 4.0,
    "issue_title": 4.0,
    "pattern_name": 4.0,
    "name": 4.0,
    "title": 4.0,
    "root_cause": 5.0,
    "broken_invariants": 3.5,
    "summary": 2.0,
    "description": 2.5,
    "issue_claim": 4.0,
    "why_it_looked_bad": 2.5,
    "why_not_valid": 3.0,
    "tags": 3.0,
    "component_types": 2.5,
    "component_type": 4.0,
    "core_invariants": 3.5,
    "trust_boundaries": 2.0,
    "common_bug_classes": 2.5,
    "check_items": 3.0,
    "test_ideas": 2.0,
    "related_pattern_ids": 1.0,
    "common_triggers": 2.0,
    "preconditions": 1.5,
    "typical_impact": 1.5,
    "validation_methods": 1.0,
    "goal": 3.0,
    "setup_requirements": 1.5,
    "minimal_state": 2.0,
    "attacker_actions": 2.0,
    "assertions": 2.5,
    "common_failures": 1.5,
    "notes": 1.0,
    "mitigations": 1.0,
    "common_false_positive_angles": 1.5,
}
_CONFIG_PATH = _REPO_ROOT / "configs" / "retrieval.yaml"


@lru_cache(maxsize=1)
def _retrieval_config() -> dict[str, Any]:
    if not _CONFIG_PATH.exists():
        return {}
    try:
        import yaml

        with _CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _field_weights() -> dict[str, float]:
    configured = _retrieval_config().get("field_weights", {})
    if not isinstance(configured, dict):
        return DEFAULT_FIELD_WEIGHTS
    weights = DEFAULT_FIELD_WEIGHTS.copy()
    for key, value in configured.items():
        try:
            weights[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    return weights


def _positive_limit() -> int:
    value = _retrieval_config().get("retrieval", {}).get("positive_limit", 8)
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 8


def _caution_limit() -> int:
    value = _retrieval_config().get("retrieval", {}).get("caution_limit", 5)
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 5


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "their",
    "this",
    "to",
    "with",
    "without",
}


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text) if len(t) > 1 and t.lower() not in STOPWORDS]


def _flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(_flatten(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_flatten(item) for item in value.values())
    return str(value)


@lru_cache(maxsize=len(DOCUMENT_SETS))
def _load_documents(document_type: str) -> tuple[dict[str, Any], ...]:
    directory = DOCUMENT_SETS[document_type]
    if not directory.exists():
        return ()
    documents: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_document_type"] = document_type
        data["_path"] = path
        documents.append(data)
    return tuple(documents)


def _field_score(query_terms: set[str], data: dict[str, Any]) -> tuple[float, list[str]]:
    score = 0.0
    matched_terms: set[str] = set()
    for field, weight in _field_weights().items():
        text = _flatten(data.get(field))
        if not text:
            continue
        terms = set(_tokens(text))
        overlap = query_terms & terms
        if not overlap:
            continue
        matched_terms.update(overlap)
        # sqrt dampens repeated broad fields while preserving field weights.
        score += weight * math.sqrt(len(overlap))
    return score, sorted(matched_terms)


def _runtime_metadata(data: dict[str, Any]) -> dict[str, set[str]]:
    """Infer normalized runtime dimensions without requiring every old record to be migrated.

    The data corpus started as EVM/Solidity and later gained Stellar/Soroban Rust.
    Newer records may carry explicit language/applicable_languages/tags, while older
    patterns/checklists often only expose ecosystem words in ids and tags. Keep this
    inference conservative: it is used for boosts and optional strict filtering, not
    as a replacement for source-level validation.
    """

    haystack = " ".join(
        _flatten(data.get(field))
        for field in (
            "id",
            "language",
            "applicable_languages",
            "runtime",
            "ecosystem",
            "tags",
            "component_type",
            "component_types",
            "pattern_id",
            "source_name",
        )
    ).lower()
    languages = set(_tokens(_flatten(data.get("language")))) | set(_tokens(_flatten(data.get("applicable_languages"))))
    ecosystems: set[str] = set(_tokens(_flatten(data.get("ecosystem"))))
    runtimes: set[str] = set(_tokens(_flatten(data.get("runtime"))))

    if "solidity" in haystack:
        languages.add("solidity")
        ecosystems.add("evm")
        runtimes.add("evm")
    if any(marker in haystack for marker in ("erc20", "erc4626", "erc721", "evm")):
        ecosystems.add("evm")
        runtimes.add("evm")
    if any(marker in haystack for marker in ("rust-soroban", "soroban-rust", "soroban", "stellar-rust", "stellar")):
        languages.add("rust-soroban")
        ecosystems.add("stellar")
        runtimes.add("soroban")
    return {"languages": languages, "ecosystems": ecosystems, "runtimes": runtimes}


def _runtime_targets(context: QueryContext) -> dict[str, set[str]]:
    return {
        "languages": set(_tokens(context.language or "")),
        "ecosystems": set(_tokens(context.ecosystem or "")),
        "runtimes": set(_tokens(context.runtime or "")),
    }


def _matches_runtime_context(context: QueryContext, data: dict[str, Any]) -> bool:
    targets = _runtime_targets(context)
    if not any(targets.values()):
        return True
    metadata = _runtime_metadata(data)
    for key, expected in targets.items():
        if not expected:
            continue
        known = metadata[key]
        if not known or not (expected & known):
            return False
    return True


def _context_score(context: QueryContext, data: dict[str, Any]) -> float:
    score = 0.0
    if context.component_type:
        component = context.component_type.lower()
        components = " ".join(data.get("component_types", [])).lower()
        tags = " ".join(data.get("tags", [])).lower()
        if component in components or component in tags:
            score += 2.0
    metadata = _runtime_metadata(data)
    targets = _runtime_targets(context)
    for key, expected in targets.items():
        if expected and expected & metadata[key]:
            score += 2.5
    if context.stage_name == "candidate-triage":
        if data.get("_document_type") == "case_report":
            score += 1.0
        if data.get("_document_type") == "false_positive_case":
            score += 0.75
    return score


def _source_for(data: dict[str, Any]) -> str:
    doc_type = data["_document_type"]
    return f"local://{doc_type}s/{data.get('id', data.get('pattern_id', 'unknown'))}"


def _project_match(data: dict[str, Any], score: float, matched_terms: list[str]) -> dict[str, Any]:
    doc_type = data["_document_type"]
    item = {
        "id": data.get("id") or data.get("pattern_id"),
        "document_type": doc_type,
        "score": round(score, 3),
        "matched_terms": matched_terms[:20],
        "source": _source_for(data),
        "source_url": data.get("source_url"),
        "tags": data.get("tags", []),
        "runtime_metadata": {key: sorted(value) for key, value in _runtime_metadata(data).items()},
    }
    if doc_type == "case_report":
        item.update(
            {
                "title": data.get("finding_title"),
                "severity": data.get("severity"),
                "protocol_name": data.get("protocol_name"),
                "root_cause": data.get("root_cause"),
                "broken_invariants": data.get("broken_invariants", []),
                "summary": data.get("summary"),
            }
        )
    elif doc_type == "false_positive_case":
        item.update(
            {
                "title": data.get("issue_claim"),
                "classification": data.get("classification"),
                "why_not_valid": data.get("why_not_valid"),
                "downgrade_reason": data.get("downgrade_reason"),
            }
        )
    elif doc_type == "vulnerability_pattern":
        item.update(
            {
                "title": data.get("pattern_name") or data.get("name") or data.get("title"),
                "root_cause": data.get("root_cause") or data.get("description"),
                "broken_invariants": data.get("broken_invariants", []),
                "summary": data.get("summary") or data.get("description"),
                "severity_baseline": data.get("severity_baseline"),
            }
        )
    elif doc_type == "component_checklist":
        item.update(
            {
                "title": data.get("component_type"),
                "summary": data.get("description"),
                "core_invariants": data.get("core_invariants", []),
                "check_items": data.get("check_items", []),
                "common_bug_classes": data.get("common_bug_classes", []),
            }
        )
    else:
        item.update({"title": data.get("title") or data.get("name"), "summary": data.get("summary")})
    return item


def _rank(query: str, context: QueryContext, document_types: list[str], limit: int) -> list[dict[str, Any]]:
    query_terms = set(_tokens(query))
    if context.component_type:
        query_terms.update(_tokens(context.component_type))
    matches: list[dict[str, Any]] = []
    for document_type in document_types:
        for data in _load_documents(document_type):
            if context.strict_runtime and not _matches_runtime_context(context, data):
                continue
            lexical_score, matched_terms = _field_score(query_terms, data)
            if lexical_score <= 0:
                continue
            score = lexical_score + _context_score(context, data)
            matches.append(_project_match(data, score, matched_terms))
    matches.sort(key=lambda item: (-item["score"], item.get("id") or ""))
    return matches[:limit]


def hybrid_search(query: str, context: QueryContext | None = None) -> dict[str, Any]:
    """Lexical-first local retrieval over normalized audit-rag JSON records.

    This is the minimum useful implementation before embeddings: structured fields are
    weighted, positive evidence is kept separate from false-positive/downgrade caution
    evidence, and the query context can add lightweight component/stage boosts.
    """

    runtime = context or QueryContext()
    positive_matches = _rank(
        query,
        runtime,
        ["case_report", "vulnerability_pattern", "component_checklist", "validation_recipe"],
        limit=_positive_limit(),
    )
    caution_matches = (
        _rank(query, runtime, ["false_positive_case"], limit=_caution_limit())
        if runtime.require_false_positive_check
        else []
    )
    return {
        "query": query,
        "status": "ok",
        "retrieval_mode": "lexical-first",
        "skill_name": runtime.skill_name,
        "stage_name": runtime.stage_name,
        "component_type": runtime.component_type,
        "ecosystem": runtime.ecosystem,
        "language": runtime.language,
        "runtime": runtime.runtime,
        "strict_runtime": runtime.strict_runtime,
        "positive_matches": positive_matches,
        "caution_matches": caution_matches,
        "message": (
            f"Retrieved {len(positive_matches)} positive matches and "
            f"{len(caution_matches)} caution matches from local normalized data."
        ),
    }
