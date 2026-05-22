from __future__ import annotations

import typer
from audit_rag.contest.lead_ledger import (
    add_lead,
    export_contest_summary,
    get_lead,
    list_leads,
    mirror_to_contest_repo,
    promote_provisional,
    update_lead_record,
)
from audit_rag.contest.scorecard import suppress_check, triage_and_persist
from audit_rag.ingestion.pipelines.ingest_reports import run_ingest
from audit_rag.quality.data_quality import validate_normalized_data
from audit_rag.retrieval.issue_triage import triage_issue
from audit_rag.retrieval.query_context import QueryContext
from audit_rag.services.output_formatter import to_pretty_json
from audit_rag.wiki.exporter import export_wiki

app = typer.Typer(help="audit-rag CLI")


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _query_context(
    skill_name: str,
    stage_name: str,
    component_type: str | None,
    ecosystem: str | None,
    language: str | None,
    runtime: str | None,
    strict_runtime: bool,
    audit_goal: str,
    desired_output_schema: str,
    require_false_positive_check: bool,
) -> QueryContext:
    return QueryContext(
        skill_name=skill_name,
        stage_name=stage_name,
        component_type=component_type,
        ecosystem=ecosystem,
        language=language,
        runtime=runtime,
        strict_runtime=strict_runtime,
        audit_goal=audit_goal,
        desired_output_schema=desired_output_schema,
        require_false_positive_check=require_false_positive_check,
    )


@app.command()
def ingest(source_dir: str) -> None:
    """Ingest raw report sources."""
    run_ingest(source_dir)


@app.command("triage-issue")
def triage_issue_cmd(
    text: str,
    skill_name: str = typer.Option("contest-audit", help="Workflow/skill name for retrieval context."),
    stage_name: str = typer.Option("candidate-triage", help="Audit stage name."),
    component_type: str | None = typer.Option(None, help="Optional component family, e.g. cross-domain-bridge."),
    ecosystem: str | None = typer.Option(None, help="Optional ecosystem, e.g. evm, stellar, sui, cosmos."),
    language: str | None = typer.Option(None, help="Optional contract language/runtime language, e.g. solidity, rust-soroban, move."),
    runtime: str | None = typer.Option(None, help="Optional execution runtime, e.g. evm, soroban, move-vm, cosmwasm."),
    strict_runtime: bool = typer.Option(
        False,
        "--strict-runtime/--soft-runtime",
        help="When enabled, exclude records with known conflicting ecosystem/language/runtime metadata.",
    ),
    audit_goal: str = typer.Option(
        "judge whether this lead is submission-worthy",
        help="What the triage should optimize for.",
    ),
    desired_output_schema: str = typer.Option(
        "candidate-triage-v1",
        help="Desired output contract/schema name.",
    ),
    require_false_positive_check: bool = typer.Option(
        True,
        "--false-positive-check/--no-false-positive-check",
        help="Whether to retrieve false-positive/downgrade caution matches.",
    ),
) -> None:
    """Triage a free-form candidate issue statement without persisting it."""
    context = _query_context(
        skill_name,
        stage_name,
        component_type,
        ecosystem,
        language,
        runtime,
        strict_runtime,
        audit_goal,
        desired_output_schema,
        require_false_positive_check,
    )
    result = triage_issue(text, context)
    print(to_pretty_json(result))


@app.command("add-lead")
def add_lead_cmd(
    contest_slug: str = typer.Argument(..., help="Contest slug, e.g. 2026-04-monetrix."),
    title: str = typer.Argument(..., help="Short lead title."),
    text: str | None = typer.Option(None, help="Detailed candidate issue statement. Defaults to title."),
    component: str | None = typer.Option(None, help="Component family, e.g. cross-domain-bridge."),
    files: str | None = typer.Option(None, help="Comma-separated current repo file paths."),
    functions: str | None = typer.Option(None, help="Comma-separated function names."),
    severity_guess: str = typer.Option("unclear", help="Initial severity guess."),
    status: str = typer.Option("new", help="Initial lead status."),
) -> None:
    """Append a candidate lead to data/provisional/contests/<slug>/lead-ledger.jsonl."""
    result = add_lead(
        contest_slug=contest_slug,
        title=title,
        text=text,
        component=component,
        files=_split_csv(files),
        functions=_split_csv(functions),
        severity_guess=severity_guess,
        status=status,
    )
    print(to_pretty_json(result))


@app.command("list-leads")
def list_leads_cmd(
    contest_slug: str = typer.Argument(..., help="Contest slug."),
    status: str | None = typer.Option(None, help="Optional status filter."),
) -> None:
    """List leads in a contest ledger."""
    print(to_pretty_json(list_leads(contest_slug, status=status)))


@app.command("update-lead")
def update_lead_cmd(
    contest_slug: str = typer.Argument(..., help="Contest slug."),
    lead_id: str = typer.Argument(..., help="Lead id from the ledger."),
    status: str | None = typer.Option(None, help="New lead status."),
    severity_guess: str | None = typer.Option(None, help="Updated severity guess."),
    current_blocker: str | None = typer.Option(None, help="Current blocker or next missing evidence."),
    duplicate_check: str | None = typer.Option(None, help="Duplicate / known finding overlap note."),
    false_positive_risk: str | None = typer.Option(None, help="False-positive or downgrade risk note."),
    validation_command: str | None = typer.Option(None, help="Latest validation command."),
    poc_path: str | None = typer.Option(None, help="Path to local PoC/test artifact."),
    final_decision: str | None = typer.Option(None, help="Final decision or reviewer-facing status."),
) -> None:
    """Update lead state after manual review, PoC, duplicate check, or final decision."""
    result = update_lead_record(
        contest_slug,
        lead_id,
        {
            "status": status,
            "severity_guess": severity_guess,
            "current_blocker": current_blocker,
            "duplicate_check": duplicate_check,
            "false_positive_risk": false_positive_risk,
            "validation_command": validation_command,
            "poc_path": poc_path,
            "final_decision": final_decision,
        },
    )
    print(to_pretty_json(result))


@app.command("triage-lead")
def triage_lead_cmd(
    contest_slug: str = typer.Argument(..., help="Contest slug."),
    lead_id: str = typer.Argument(..., help="Lead id from the ledger."),
    skill_name: str = typer.Option("contest-audit", help="Workflow/skill name for retrieval context."),
    stage_name: str = typer.Option("candidate-triage", help="Audit stage name."),
    component_type: str | None = typer.Option(None, help="Override component family."),
    ecosystem: str | None = typer.Option(None, help="Optional ecosystem."),
    language: str | None = typer.Option(None, help="Optional language."),
    runtime: str | None = typer.Option(None, help="Optional execution runtime."),
    strict_runtime: bool = typer.Option(False, "--strict-runtime/--soft-runtime"),
    require_false_positive_check: bool = typer.Option(True, "--false-positive-check/--no-false-positive-check"),
) -> None:
    """Run RAG-backed scorecard triage for a persisted lead and save raw output."""
    lead = get_lead(contest_slug, lead_id)
    context = _query_context(
        skill_name,
        stage_name,
        component_type or lead.component,
        ecosystem,
        language,
        runtime,
        strict_runtime,
        "judge whether this lead is submission-worthy",
        "lead-triage-scorecard-v1",
        require_false_positive_check,
    )
    print(to_pretty_json(triage_and_persist(lead, context)))


@app.command("suppress-check")
def suppress_check_cmd(
    contest_slug: str = typer.Argument(..., help="Contest slug."),
    lead_id: str = typer.Argument(..., help="Lead id from the ledger."),
    component_type: str | None = typer.Option(None, help="Override component family."),
    ecosystem: str | None = typer.Option(None, help="Optional ecosystem."),
    language: str | None = typer.Option(None, help="Optional language."),
    runtime: str | None = typer.Option(None, help="Optional execution runtime."),
    strict_runtime: bool = typer.Option(False, "--strict-runtime/--soft-runtime"),
) -> None:
    """Check duplicate, downgrade, and false-positive suppression risks for a lead."""
    lead = get_lead(contest_slug, lead_id)
    context = _query_context(
        "contest-audit",
        "candidate-triage",
        component_type or lead.component,
        ecosystem,
        language,
        runtime,
        strict_runtime,
        "identify whether this lead should be suppressed, downgraded, or validated further",
        "suppression-check-v1",
        True,
    )
    print(to_pretty_json(suppress_check(lead, context)))


@app.command("export-contest-summary")
def export_contest_summary_cmd(
    contest_slug: str = typer.Argument(..., help="Contest slug."),
) -> None:
    """Export a Markdown summary of the current contest lead ledger."""
    print(to_pretty_json(export_contest_summary(contest_slug)))


@app.command("mirror-contest-state")
def mirror_contest_state_cmd(
    contest_slug: str = typer.Argument(..., help="Contest slug."),
    contest_repo: str = typer.Argument(..., help="Active contest repository path."),
) -> None:
    """Mirror audit-rag provisional state into an active contest repo audit-context folder."""
    print(to_pretty_json(mirror_to_contest_repo(contest_slug, contest_repo)))


@app.command("promote-provisional")
def promote_provisional_cmd(
    contest_slug: str = typer.Argument(..., help="Contest slug."),
    confirmed: bool = typer.Option(
        False,
        "--confirmed/--dry-run",
        help="Actually promote records. Default dry-run writes only promotion-manifest.json.",
    ),
) -> None:
    """Promote curated provisional records to normalized data after final outcome review."""
    print(to_pretty_json(promote_provisional(contest_slug, confirmed=confirmed)))


@app.command("export-wiki")
def export_wiki_cmd(
    wiki_dir: str = typer.Option("wiki", help="Wiki directory relative to repo root."),
) -> None:
    """Export normalized JSON records into read-only Markdown pages under wiki/generated/."""
    print(to_pretty_json(export_wiki(wiki_dir=wiki_dir).to_dict()))


@app.command("validate-data")
def validate_data_cmd() -> None:
    """Validate normalized RAG data schemas and quality gates."""
    result = validate_normalized_data()
    print(to_pretty_json(result))
    if result["status"] != "ok":
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
