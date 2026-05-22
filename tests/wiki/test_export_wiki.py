from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from audit_rag.cli.main import app
from audit_rag.wiki.exporter import export_wiki

runner = CliRunner()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_export_wiki_writes_generated_markdown_from_normalized_json(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "data/normalized/vulnerability_patterns/soroban-require-auth-entrypoint-bypass-pattern.json",
        {
            "id": "soroban-require-auth-entrypoint-bypass-pattern",
            "name": "Missing require_auth across entrypoints",
            "description": "Soroban entrypoints must authenticate the consumed Address.",
            "broken_invariants": ["owner state must require owner auth"],
            "tags": ["require-auth", "soroban-rust"],
        },
    )
    _write_json(
        tmp_path / "data/normalized/false_positive_cases/soroban-helper-fp.json",
        {
            "id": "soroban-helper-fp",
            "issue_claim": "Internal helper lacks require_auth",
            "why_not_valid": "All public callers authenticate the owner first.",
            "tags": ["require-auth", "false-positive"],
        },
    )

    result = export_wiki(root_path=tmp_path)

    assert result.status == "ok"
    assert result.exported_count == 2
    generated_index = tmp_path / "wiki/generated/index.md"
    assert generated_index.exists()
    index_text = generated_index.read_text(encoding="utf-8")
    assert "soroban-require-auth-entrypoint-bypass-pattern" in index_text
    assert "soroban-helper-fp" in index_text

    pattern_page = tmp_path / "wiki/generated/vulnerability_patterns/soroban-require-auth-entrypoint-bypass-pattern.md"
    assert pattern_page.exists()
    page_text = pattern_page.read_text(encoding="utf-8")
    assert "Do not edit this page by hand" in page_text
    assert "[[concepts/soroban-require-auth|Soroban require_auth]]" in page_text


def test_export_wiki_cli_accepts_custom_wiki_dir(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path) as cwd:
        cwd_path = Path(cwd)
        _write_json(
            cwd_path / "data/normalized/validation_recipes/example-recipe.json",
            {
                "id": "example-recipe",
                "goal": "Build an auth matrix test",
                "assertions": ["unauthorized calls fail"],
            },
        )

        result = runner.invoke(app, ["export-wiki", "--wiki-dir", "notes"])
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["status"] == "ok"
        assert payload["wiki_dir"] == "notes"
        assert payload["exported_count"] == 1
        assert (cwd_path / "notes/generated/validation_recipes/example-recipe.md").exists()
