import json

from audit_rag.contest import lead_ledger
from audit_rag.contest.lead_ledger import (
    add_lead,
    export_contest_summary,
    get_lead,
    list_leads,
    promote_provisional,
    update_lead_record,
)
from audit_rag.contest.scorecard import suppress_check, triage_and_persist


def test_add_and_list_leads(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(lead_ledger, "_PROVISIONAL_DIR", tmp_path)

    result = add_lead(
        contest_slug="demo-contest",
        title="Bridge accounting clears retry state before async settlement",
        text="bridge accounting clears retry state before async settlement and funds are stuck",
        component="cross-domain-bridge",
        files=["src/Bridge.sol"],
        functions=["bridgePrincipalFromL1"],
        severity_guess="medium",
    )

    assert result["status"] == "ok"
    lead_id = result["lead"]["id"]
    listed = list_leads("demo-contest")
    assert listed["count"] == 1
    assert listed["leads"][0]["id"] == lead_id
    assert get_lead("demo-contest", lead_id).component == "cross-domain-bridge"


def test_update_lead_and_export_summary(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(lead_ledger, "_PROVISIONAL_DIR", tmp_path)
    added = add_lead("demo-contest", "Lead that needs PoC", text="possible issue")
    lead_id = added["lead"]["id"]

    updated = update_lead_record(
        "demo-contest",
        lead_id,
        {
            "status": "needs-poc",
            "current_blocker": "need runnable PoC",
            "validation_command": "forge test --match-path test/c4/C4Submission.t.sol -vvv",
        },
    )
    assert updated["lead"]["status"] == "needs-poc"

    summary = export_contest_summary("demo-contest")
    assert summary["status"] == "ok"
    assert summary["status_counts"] == {"needs-poc": 1}
    assert "contest-summary.md" in summary["summary_path"]
    assert "need runnable PoC" in (tmp_path / "demo-contest" / "contest-summary.md").read_text()


def test_triage_lead_persists_scorecard(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(lead_ledger, "_PROVISIONAL_DIR", tmp_path)

    added = add_lead(
        contest_slug="demo-contest",
        title="ERC4626 restricted owner bypasses withdrawal restrictions",
        text="A FULL_RESTRICTED staker can approve another account and use ERC4626 withdraw to bypass owner restrictions",
        component="staking",
    )
    lead = get_lead("demo-contest", added["lead"]["id"])

    result = triage_and_persist(lead)

    assert result["status"] == "ok"
    assert result["scorecard"]["matching_cases"]
    assert result["triage_path"].endswith(f"{lead.id}.json")
    updated = get_lead("demo-contest", lead.id)
    assert updated.rag_triage_path == result["triage_path"]
    assert updated.related_rag_cases


def test_suppress_check_returns_recommendation(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(lead_ledger, "_PROVISIONAL_DIR", tmp_path)

    added = add_lead(
        contest_slug="demo-contest",
        title="Owner misconfiguration causes unsupported token issue",
        text="owner admin misconfiguration uses unsupported token and causes only user mistake impact",
    )
    lead = get_lead("demo-contest", added["lead"]["id"])

    result = suppress_check(lead)

    assert result["status"] == "ok"
    assert result["kind"] == "suppression-check"
    assert result["recommendation"] in {
        "suppress-or-duplicate-review",
        "downgrade-to-qa-or-abandon",
        "needs-negative-case-review",
        "continue-validation",
    }
    assert result["suppression_signals"]


def test_promote_provisional_requires_confirmation(tmp_path, monkeypatch) -> None:
    provisional_root = tmp_path / "provisional"
    normalized_root = tmp_path / "normalized"
    monkeypatch.setattr(lead_ledger, "_PROVISIONAL_DIR", provisional_root)
    monkeypatch.setattr(lead_ledger, "_NORMALIZED_DIR", normalized_root)
    source = provisional_root / "demo-contest" / "candidate_patterns" / "demo-pattern.provisional.json"
    source.parent.mkdir(parents=True)
    source.write_text(
        json.dumps(
            {
                "candidate_record_type": "vulnerability_pattern",
                "candidate": {
                    "id": "demo-pattern",
                    "name": "Demo Pattern",
                    "category": "test-category",
                    "description": "Only a test candidate.",
                    "severity_baseline": "medium when value-moving state is affected",
                    "tags": ["test-pattern"],
                },
            }
        )
    )

    dry_run = promote_provisional("demo-contest", confirmed=False)
    assert dry_run["planned_count"] == 1
    assert dry_run["promoted_count"] == 0
    assert not (normalized_root / "vulnerability_patterns" / "demo-pattern.json").exists()

    promoted = promote_provisional("demo-contest", confirmed=True)
    assert promoted["promoted_count"] == 1
    assert (normalized_root / "vulnerability_patterns" / "demo-pattern.json").exists()
