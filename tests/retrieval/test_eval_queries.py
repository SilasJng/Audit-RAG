import json
from pathlib import Path

from audit_rag.indexing.hybrid_search import hybrid_search
from audit_rag.retrieval.query_context import QueryContext


EVAL_PATH = Path(__file__).resolve().parents[2] / "data" / "eval" / "retrieval_queries.jsonl"


def test_retrieval_eval_queries_hit_expected_ids() -> None:
    failures: list[str] = []
    for line_number, line in enumerate(EVAL_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        row = json.loads(line)
        result = hybrid_search(row["query"], QueryContext(require_false_positive_check=True))
        positive_ids = [item["id"] for item in result["positive_matches"]]
        caution_ids = [item["id"] for item in result["caution_matches"]]

        expected_top_ids = row.get("expected_top_ids", [])
        expected_document_types = row.get("expected_document_types", [])
        positive_document_types = [item["document_type"] for item in result["positive_matches"]]

        missing_positive = [item for item in row.get("expected_positive_ids", []) if item not in positive_ids]
        missing_caution = [item for item in row.get("expected_caution_ids", []) if item not in caution_ids]
        missing_top = [item for item in expected_top_ids if item not in positive_ids[: len(expected_top_ids)]]
        missing_document_types = [
            item for item in expected_document_types if item not in positive_document_types
        ]
        if missing_positive or missing_caution or missing_top or missing_document_types:
            failures.append(
                f"line {line_number} {row.get('id')}: "
                f"missing_positive={missing_positive}, positive_ids={positive_ids}; "
                f"missing_caution={missing_caution}, caution_ids={caution_ids}; "
                f"missing_top={missing_top}, expected_top_ids={expected_top_ids}; "
                f"missing_document_types={missing_document_types}, "
                f"positive_document_types={positive_document_types}"
            )

    assert not failures, "\n".join(failures)
