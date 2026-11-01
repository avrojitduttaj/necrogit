import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import git
from click.testing import CliRunner

from necrogit.cli import cli
from necrogit.core.backboard import BackboardMemory

def test_e2e_external_arbitrary_repo_with_spaces():
    """End-to-end acceptance test:
    Running NecroGit CLI commands from an external arbitrary git repository
    at a path with spaces, verifying zero pollution of unapplied files,
    accurate maintainer essence recovery, AST bitrot discovery, and clean exits.
    """
    runner = CliRunner()

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        temp_root = Path(tmp_dir)
        # Create an external repository path with spaces
        external_repo = temp_root / "external workspace with spaces" / "ancient legacy project"
        external_repo.mkdir(parents=True)

        # Initialize git repository
        repo = git.Repo.init(str(external_repo))
        repo.config_writer().set_value("user", "name", "Ada Lovelace").release()
        repo.config_writer().set_value("user", "email", "ada@lovelace.org").release()

        # Add a legacy Python script
        legacy_file = external_repo / "archaic_pipeline.py"
        legacy_code = (
            '"""Legacy pipeline module with PEP 594 removals."""\n'
            'import imp\n'
            'import pipes\n'
            'import time\n\n'
            'def run_stream(cmd):\n'
            '    start = time.clock()\n'
            '    quoted = pipes.quote(cmd)\n'
            '    module = imp.find_module("sys")\n'
            '    return start, quoted, module\n'
        )
        legacy_file.write_text(legacy_code, encoding="utf-8")

        # Commit legacy code
        repo.index.add(["archaic_pipeline.py"])
        repo.index.commit("Archival commit from 1843: implement difference engine stream")

        # Isolated memory home so tests don't touch actual user home
        isolated_home = temp_root / "user_home"
        isolated_home.mkdir()

        with patch.dict(os.environ, {"NECROGIT_HOME": str(isolated_home)}):
            # 1. Run necrogit --help
            res_help = runner.invoke(cli, ["--help"])
            assert res_help.exit_code == 0
            assert "NecroGit: The Repository Medium" in res_help.output

            # 2. Run necrogit inspect . in target repo
            with runner.isolation():
                # We pass the target directory explicitly or invoke inside it
                res_inspect = runner.invoke(cli, ["inspect", str(external_repo)])
                assert res_inspect.exit_code == 0
                assert "archaic_pipeline.py" in res_inspect.output
                assert "imp" in res_inspect.output
                assert "pipes" in res_inspect.output
                assert "time.clock" in res_inspect.output

            # 3. Run necrogit summon . in target repo
            res_summon = runner.invoke(cli, ["summon", str(external_repo)])
            assert res_summon.exit_code == 0
            assert "Ada Lovelace" in res_summon.output
            assert "difference engine stream" in res_summon.output

            # 4. Run necrogit patch . (directory argument) -> should warn gracefully and list candidate
            res_patch_dir = runner.invoke(cli, ["patch", str(external_repo)])
            assert res_patch_dir.exit_code == 0
            assert "is a directory" in res_patch_dir.output
            assert "archaic_pipeline.py" in res_patch_dir.output

            # 5. Run necrogit explain . (directory argument) -> should warn gracefully and list candidate
            res_explain_dir = runner.invoke(cli, ["explain", str(external_repo)])
            assert res_explain_dir.exit_code == 0
            assert "is a directory" in res_explain_dir.output
            assert "archaic_pipeline.py" in res_explain_dir.output

            # 6. Run necrogit memory -> should show Ada Lovelace dossier
            res_memory = runner.invoke(cli, ["memory"])
            assert res_memory.exit_code == 0
            assert "Ada Lovelace" in res_memory.output

            # 7. CRITICAL VERIFICATION: Target repository must have ZERO untracked files or pollution
            # No .necrogit was dumped inside the external repo, original file untouched
            assert len(repo.untracked_files) == 0
            assert repo.is_dirty() is False
            assert legacy_file.read_text(encoding="utf-8") == legacy_code

            # 8. Test necrogit patch on target file with simulated LLM response
            mock_post = MagicMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "choices": [{
                    "message": {
                        "content": (
                            "--- a/archaic_pipeline.py\n"
                            "+++ b/archaic_pipeline.py\n"
                            "@@ -1,4 +1,4 @@\n"
                            "-import imp\n"
                            "+import importlib\n"
                        )
                    }
                }]
            }
            mock_post.return_value = mock_resp

            with patch("httpx.Client.post", mock_post):
                res_patch_file = runner.invoke(
                    cli,
                    ["patch", str(legacy_file), "--repo", str(external_repo), "--apply"]
                )
                assert res_patch_file.exit_code == 0
                assert "Ethereal Unified Diff" in res_patch_file.output
                assert (external_repo / "archaic_pipeline.patch").exists()

                # Verify original file was not mutated silently (patch is in .patch file for git apply)
                assert legacy_file.read_text(encoding="utf-8") == legacy_code

        # Explicitly close repo to release Windows file locks
        repo.close()
