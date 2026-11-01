import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from necrogit.telemetry import trace_span, record_breadcrumb

class BackboardMemory:
    """Persistent memory management for NecroGit séances and repository dossiers.
    
    Provides persistent state across CLI runs, supporting both local air-gapped storage
    and Backboard (R-CLI / backboard.io) cloud synchronization when configured.
    """

    def __init__(self, workspace_root: Optional[Any] = None):
        if workspace_root is not None:
            self.storage_dir = Path(workspace_root).resolve() / ".necrogit"
        else:
            local_necrogit = Path.cwd() / ".necrogit"
            if local_necrogit.is_dir():
                self.storage_dir = local_necrogit.resolve()
            else:
                custom_home = os.getenv("NECROGIT_HOME")
                base_dir = Path(custom_home).resolve() if custom_home else Path.home()
                self.storage_dir = base_dir / ".necrogit"
        self.workspace_root = self.storage_dir.parent
        self.storage_file = self.storage_dir / "seance_memory.json"
        self.api_key = os.getenv("BACKBOARD_API_KEY")
        self.base_url = os.getenv("BACKBOARD_BASE_URL", "https://app.backboard.io/api").rstrip("/")
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Ensure the local .necrogit directory and storage file exist."""
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            if not self.storage_file.exists():
                self.storage_file.write_text(json.dumps({"dossiers": {}, "version": "1.0"}, indent=2), encoding="utf-8")
        except Exception:
            pass

    def save_dossier(self, repo_key: str, persona: Dict[str, Any], relics_count: int, last_action: str) -> Dict[str, Any]:
        """Persist a repository séance dossier locally and attempt Backboard sync if active."""
        with trace_span("necrogit.backboard", "save_dossier", {"repo_key": repo_key}):
            record_breadcrumb("backboard", f"Persisting séance memory for {repo_key}", data={"relics": relics_count})
            
            dossier = {
                "repo_key": repo_key,
                "maintainer": persona.get("maintainer", "Unknown"),
                "temperament": persona.get("brevity", "laconic"),
                "last_active": persona.get("last_active", "Unknown"),
                "commit_count": persona.get("commit_count", 0),
                "relics_count": relics_count,
                "last_action": last_action,
            }

            # 1. Local persistent storage
            try:
                data = json.loads(self.storage_file.read_text(encoding="utf-8"))
            except Exception:
                data = {"dossiers": {}, "version": "1.0"}

            data["dossiers"][repo_key] = dossier
            try:
                self.storage_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception:
                pass

            # 2. Remote Backboard synchronization if API key is provided
            if self.api_key:
                self._sync_remote(repo_key, dossier)

            return dossier

    def get_dossier(self, repo_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a stored dossier by repository key."""
        try:
            if not self.storage_file.exists():
                return None
            data = json.loads(self.storage_file.read_text(encoding="utf-8"))
            return data.get("dossiers", {}).get(repo_key)
        except Exception:
            return None

    def list_dossiers(self) -> Dict[str, Any]:
        """List all known repository dossiers currently in persistent memory."""
        try:
            if not self.storage_file.exists():
                return {}
            data = json.loads(self.storage_file.read_text(encoding="utf-8"))
            return data.get("dossiers", {})
        except Exception:
            return {}

    def clear(self) -> None:
        """Clear all stored dossiers from local persistent memory."""
        try:
            self.storage_file.write_text(json.dumps({"dossiers": {}, "version": "1.0"}, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _sync_remote(self, repo_key: str, dossier: Dict[str, Any]) -> bool:
        """Sync dossier to Backboard platform state."""
        with trace_span("necrogit.backboard", "remote_sync", {"repo_key": repo_key}):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "name": f"necrogit-{repo_key}",
                    "state": dossier
                }
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(f"{self.base_url}/state", json=payload, headers=headers)
                    return resp.is_success
            except Exception:
                return False
