import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import git
import httpx
from click.testing import CliRunner

from necrogit.core.archaeology import inspect_file, inspect_directory
from necrogit.core.persona import MaintainerMedium
from necrogit.core.engine import SeanceEngine
from necrogit.core.backboard import BackboardMemory
from necrogit.telemetry import record_breadcrumb, set_agent_context
from necrogit.cli import cli

def test_archaeology_detects_deprecated_imports():
    legacy_code = "import imp\nimport pipes\nimport os\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(legacy_code)
        tmp_path = Path(tmp.name)

    try:
        findings = inspect_file(tmp_path)
        targets = [f["target"] for f in findings]
        assert "imp" in targets
        assert "pipes" in targets
        assert "os" not in targets
    finally:
        tmp_path.unlink()

def test_persona_non_git_directory(tmp_path):
    medium = MaintainerMedium(str(tmp_path))
    persona = medium.summon_maintainer_essence()
    assert persona["is_git"] is False
    assert persona["maintainer"] == "Unknown Spirit"

@patch("httpx.Client.post")
def test_engine_prompt_payload_construction(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "--- a/test.py\n+++ b/test.py"}}]
    }
    mock_post.return_value = mock_response

    engine = SeanceEngine()
    persona = {"maintainer": "Ada Lovelace", "last_active": "1852-11-27", "brevity": "laconic"}
    diff = engine.consult_ghost(persona, "import imp", "Line 1: imp is removed")

    assert "--- a/test.py" in diff
    call_args = mock_post.call_args[1]
    system_prompt = call_args["json"]["messages"][0]["content"]
    assert "Ada Lovelace" in system_prompt

@patch("httpx.Client.post")
def test_engine_explain_design_construction(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "In 2008, GIL contention necessitated manual pipe buffers."}}]
    }
    mock_post.return_value = mock_response

    engine = SeanceEngine(model="gemma2:9b")
    persona = {"maintainer": "Guido van Rossum", "last_active": "2018-07-12", "brevity": "philosophical"}
    explanation = engine.explain_design(persona, "import pipes", symbol_query="format_pipeline")

    assert "GIL contention" in explanation
    call_args = mock_post.call_args[1]
    system_prompt = call_args["json"]["messages"][0]["content"]
    user_prompt = call_args["json"]["messages"][1]["content"]
    assert "Guido van Rossum" in system_prompt
    assert "format_pipeline" in user_prompt

def test_archaeology_detects_syntax_rot(tmp_path):
    broken_code = "def syntax_horror(\n    print('unclosed function'\n"
    bad_file = tmp_path / "broken.py"
    bad_file.write_text(broken_code, encoding="utf-8")

    findings = inspect_file(bad_file)
    assert len(findings) == 1
    assert findings[0]["target"] == "SyntaxError"
    assert findings[0]["type"] == "syntax_rot"

def test_archaeology_inspect_directory(tmp_path):
    sub = tmp_path / "legacy_module"
    sub.mkdir()
    f1 = sub / "mod1.py"
    f1.write_text("import cgi\nimport time\n_ = time.clock()\n", encoding="utf-8")
    f2 = sub / "clean.py"
    f2.write_text("import sys\nimport pathlib\n", encoding="utf-8")

    report = inspect_directory(tmp_path)
    rel_path = str(f1.relative_to(tmp_path))
    clean_rel = str(f2.relative_to(tmp_path))

    assert rel_path in report
    assert clean_rel not in report
    targets = [item["target"] for item in report[rel_path]]
    assert "cgi" in targets
    assert "time.clock" in targets

def test_persona_git_repo(tmp_path):
    repo = git.Repo.init(str(tmp_path))
    test_file = tmp_path / "relic.txt"
    test_file.write_text("Initial relic", encoding="utf-8")
    repo.index.add(["relic.txt"])
    author = git.Actor("Grace Hopper", "grace@navy.mil")
    repo.index.commit("Found first computer bug in relay #70", author=author, committer=author)

    medium = MaintainerMedium(str(tmp_path))
    persona = medium.summon_maintainer_essence()
    assert persona["is_git"] is True
    assert persona["maintainer"] == "Grace Hopper"
    assert persona["commit_count"] == 1
    assert len(persona["sample_logs"]) == 1
    assert "Found first computer bug" in persona["sample_logs"][0]

@patch("httpx.Client.post")
def test_engine_connect_error(mock_post):
    mock_post.side_effect = httpx.ConnectError("Connection refused")
    engine = SeanceEngine(base_url="http://localhost:99999/v1")
    persona = {"maintainer": "Bjarne", "last_active": "2000-01-01", "brevity": "terse"}
    result = engine.consult_ghost(persona, "import imp", "Line 1: imp is gone")
    assert "Séance Severed" in result

def test_backboard_memory_local_persistence(tmp_path):
    mem = BackboardMemory(workspace_root=tmp_path)
    persona = {
        "maintainer": "Margaret Hamilton",
        "brevity": "terse",
        "last_active": "1969-07-20",
        "commit_count": 42
    }
    dossier = mem.save_dossier("apollo-11", persona, relics_count=3, last_action="summon")
    assert dossier["maintainer"] == "Margaret Hamilton"

    retrieved = mem.get_dossier("apollo-11")
    assert retrieved is not None
    assert retrieved["commit_count"] == 42
    assert retrieved["relics_count"] == 3

    all_dossiers = mem.list_dossiers()
    assert "apollo-11" in all_dossiers

def test_telemetry_breadcrumbs_and_context():
    # Should run cleanly without raising exceptions whether Sentry is active or not
    record_breadcrumb("test_cat", "Test breadcrumb message", data={"sample": 1})
    set_agent_context("test_agent", {"version": "0.1.0"})

def test_cli_summon_inspect_explain_and_memory(tmp_path):
    runner = CliRunner()
    
    # 1. Summon on non-git dir
    res_summon = runner.invoke(cli, ["summon", str(tmp_path)])
    assert res_summon.exit_code == 0
    assert "No git presence detected" in res_summon.output

    # 2. Inspect bitrot
    py_file = tmp_path / "obsolete.py"
    py_file.write_text("import distutils\nimport imp\n", encoding="utf-8")
    res_inspect = runner.invoke(cli, ["inspect", str(tmp_path)])
    assert res_inspect.exit_code == 0
    assert "distutils" in res_inspect.output
    assert "imp" in res_inspect.output

    # 3. Memory inspection
    res_mem = runner.invoke(cli, ["memory"])
    assert res_mem.exit_code == 0
    assert "Backboard Persistent Memory" in res_mem.output
