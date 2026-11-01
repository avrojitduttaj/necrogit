import tempfile
import zipfile
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

@patch("httpx.Client.post")
def test_engine_http_404_error(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "404 Not Found"
    mock_post.return_value = mock_resp

    engine = SeanceEngine(base_url="http://localhost:11434/v1")
    persona = {"maintainer": "Dennis Ritchie", "last_active": "2011-10-12", "brevity": "laconic"}
    result = engine.consult_ghost(persona, "import imp", "imp removed")
    assert "404 Not Found" in result or "Endpoint" in result

@patch("httpx.Client.post")
def test_engine_model_not_found_404(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "model 'gemma2:9b' not found, try pulling it first"
    mock_post.return_value = mock_resp

    engine = SeanceEngine(model="gemma2:9b")
    persona = {"maintainer": "Linus Torvalds", "last_active": "2026-01-01", "brevity": "direct"}
    result = engine.consult_ghost(persona, "import imp", "imp removed")
    assert "Model Absent" in result or "ollama pull" in result

@patch("httpx.Client.post")
def test_engine_native_ollama_fallback(mock_post):
    # Primary /v1/chat/completions returns 404, fallback /api/chat returns 200
    resp_primary = MagicMock()
    resp_primary.status_code = 404
    resp_primary.text = "404 Not Found"

    resp_fallback = MagicMock()
    resp_fallback.status_code = 200
    resp_fallback.json.return_value = {
        "message": {"role": "assistant", "content": "--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n-import imp\n+import importlib"}
    }

    mock_post.side_effect = [resp_primary, resp_fallback]

    engine = SeanceEngine(base_url="http://localhost:11434/v1")
    persona = {"maintainer": "Ada Lovelace", "last_active": "1852-11-27", "brevity": "laconic"}
    result = engine.consult_ghost(persona, "import imp", "Line 1: imp is removed")
    assert "--- a/test.py" in result
    assert "+import importlib" in result

@patch("httpx.Client.post")
def test_engine_malformed_response(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"unrecognized_key": []}
    mock_post.return_value = mock_resp

    engine = SeanceEngine()
    persona = {"maintainer": "Ada Lovelace", "last_active": "1852-11-27", "brevity": "laconic"}
    result = engine.consult_ghost(persona, "import imp", "Line 1: imp is removed")
    assert "Malformed Response" in result

@patch("httpx.Client.post")
def test_engine_timeout(mock_post):
    mock_post.side_effect = httpx.TimeoutException("Read timed out")
    engine = SeanceEngine()
    persona = {"maintainer": "Ada Lovelace", "last_active": "1852-11-27", "brevity": "laconic"}
    result = engine.consult_ghost(persona, "import imp", "Line 1: imp is removed")
    assert "Timeout" in result

@patch("httpx.Client.get")
def test_engine_check_health(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [{"name": "gemma2:9b"}, {"name": "llama3.2:3b"}]
    }
    mock_get.return_value = mock_resp

    engine = SeanceEngine(model="gemma2:9b")
    health = engine.check_health()
    assert health["connected"] is True
    assert health["model_found"] is True

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

    mem.clear()
    assert len(mem.list_dossiers()) == 0

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

    # 3. Bare memory invocation (empty state)
    res_mem = runner.invoke(cli, ["memory"])
    assert res_mem.exit_code == 0
    assert "Backboard Persistent Memory" in res_mem.output

def test_cli_memory_populated_and_clear(tmp_path):
    runner = CliRunner()
    # Save a dossier directly into memory store
    mem = BackboardMemory()
    mem.save_dossier("demo_repo", {"maintainer": "Alan Turing", "brevity": "mathematical", "last_active": "1954", "commit_count": 99}, relics_count=4, last_action="summon")

    res_mem = runner.invoke(cli, ["memory"])
    assert res_mem.exit_code == 0
    assert "Alan Turing" in res_mem.output

    # Test clear
    res_clear = runner.invoke(cli, ["memory", "--clear"])
    assert res_clear.exit_code == 0
    assert "cleared" in res_clear.output

def test_cli_export_web(tmp_path):
    runner = CliRunner()
    export_target = tmp_path / "web_export"
    result = runner.invoke(cli, ["export-web", str(export_target)])
    assert result.exit_code == 0
    assert "Exported NecroGit web assets" in result.output
    index_file = export_target / "index.html"
    assert index_file.exists()
    assert "NecroGit" in index_file.read_text(encoding="utf-8")

def test_cli_export_web_paths_with_spaces_and_zip(tmp_path):
    runner = CliRunner()
    export_target = tmp_path / "target folder with spaces" / "site export"
    result = runner.invoke(cli, ["export-web", str(export_target)])
    assert result.exit_code == 0
    assert "Exported NecroGit web assets" in result.output

    # Verify files in folder with spaces
    assert (export_target / "index.html").exists()
    assert (export_target / "style.css").exists()
    assert (export_target / "app.js").exists()
    assert (export_target / "README.md").exists()

    # Verify ZIP bundle was generated and contains valid contents
    zip_bundle = export_target / "necrogit-site.zip"
    assert zip_bundle.exists()
    with zipfile.ZipFile(zip_bundle, "r") as zf:
        namelist = zf.namelist()
        assert "index.html" in namelist
        assert "style.css" in namelist

    # Test repeated export (idempotency)
    result_repeat = runner.invoke(cli, ["export-web", str(export_target)])
    assert result_repeat.exit_code == 0
    assert (export_target / "index.html").exists()

def test_cli_doctor():
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code == 0
    assert "NecroGit System Diagnostics" in result.output
    assert "Python Environment" in result.output

def test_cli_directory_handling_for_patch_and_explain(tmp_path):
    runner = CliRunner()
    proj = tmp_path / "legacy_dir"
    proj.mkdir()
    relic = proj / "ancient.py"
    relic.write_text("import imp\nimport pipes\n", encoding="utf-8")

    # Patch on directory
    res_patch = runner.invoke(cli, ["patch", str(proj)])
    assert res_patch.exit_code == 0
    assert "is a directory" in res_patch.output
    assert "ancient.py" in res_patch.output

    # Explain on directory
    res_explain = runner.invoke(cli, ["explain", str(proj)])
    assert res_explain.exit_code == 0
    assert "is a directory" in res_explain.output
    assert "ancient.py" in res_explain.output

    # Inspect single file
    res_inspect_file = runner.invoke(cli, ["inspect", str(relic)])
    assert res_inspect_file.exit_code == 0
    assert "ancient.py" in res_inspect_file.output
    assert "imp" in res_inspect_file.output

