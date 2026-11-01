from collections import Counter
from pathlib import Path
from typing import Dict, Any, List, Union
import git
from necrogit.telemetry import trace_span

class MaintainerMedium:
    """Extracts historical telemetry from Git to construct a maintainer persona."""

    def __init__(self, repo_path: Union[str, Path] = "."):
        self.repo_path = Path(repo_path).resolve()
        try:
            self.repo = git.Repo(self.repo_path, search_parent_directories=True)
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            self.repo = None

    def summon_maintainer_essence(self, max_commits: int = 100) -> Dict[str, Any]:
        """Channel git logs to divine the primary maintainer's coding cadence and spirit."""
        with trace_span("necrogit.persona", "mine_git_history"):
            if not self.repo:
                return {
                    "maintainer": "Unknown Spirit",
                    "commit_count": 0,
                    "brevity": "moderate",
                    "sample_logs": [],
                    "last_active": "Time immemorial",
                    "is_git": False
                }

            try:
                commits: List[git.Commit] = list(self.repo.iter_commits(max_count=max_commits))
            except Exception:
                commits = []

            if not commits:
                return {
                    "maintainer": "Empty Void",
                    "commit_count": 0,
                    "brevity": "laconic",
                    "sample_logs": [],
                    "last_active": "Never",
                    "is_git": True
                }

            authors = Counter([c.author.name for c in commits if c.author and c.author.name])
            if not authors:
                primary_author, count = "Anonymous Entity", len(commits)
            else:
                primary_author, count = authors.most_common(1)[0]

            messages = [
                c.message.strip().split("\n")[0]
                for c in commits
                if c.author and c.author.name == primary_author and c.message.strip()
            ]
            
            avg_len = sum(len(m) for m in messages) / max(len(messages), 1)
            brevity = "terse/laconic" if avg_len < 30 else ("verbose" if avg_len > 70 else "balanced")

            last_active = "Never"
            if commits:
                try:
                    last_active = commits[0].committed_datetime.strftime("%Y-%m-%d")
                except Exception:
                    last_active = "Unknown date"

            return {
                "maintainer": primary_author,
                "commit_count": count,
                "brevity": brevity,
                "sample_logs": messages[:6],
                "last_active": last_active,
                "total_analyzed": len(commits),
                "is_git": True
            }
