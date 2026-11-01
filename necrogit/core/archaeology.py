import ast
from pathlib import Path
from typing import List, Dict, Any, Union
from necrogit.telemetry import trace_span

KNOWN_DEPRECATIONS: Dict[str, str] = {
    # Event loop & async legacy
    "asyncio.get_event_loop": "Deprecated in modern Python without running loop; prefer asyncio.run() or asyncio.get_running_loop()",
    # PEP 594 removals in Python 3.13
    "pipes": "Removed in Python 3.13; use subprocess or shlex",
    "cgi": "Removed in Python 3.13; use urllib.parse or email",
    "cgitb": "Removed in Python 3.13; use traceback or logging",
    "telnetlib": "Removed in Python 3.13; use telnetlib3 or socket",
    "crypt": "Removed in Python 3.13; use hashlib, passlib, or bcrypt",
    "chunk": "Removed in Python 3.13; read audio chunks directly",
    "imghdr": "Removed in Python 3.13; use filetype or puremagic",
    "mailcap": "Removed in Python 3.13; use mimetypes",
    "nis": "Removed in Python 3.13; legacy Sun NIS client",
    "nntplib": "Removed in Python 3.13; legacy NNTP news client",
    "ossaudiodev": "Removed in Python 3.13; legacy Open Sound System interface",
    "sndhdr": "Removed in Python 3.13; use soundfile or filetype",
    "spwd": "Removed in Python 3.13; legacy shadow password database",
    "sunau": "Removed in Python 3.13; use wave or soundfile",
    "uu": "Removed in Python 3.13; use base64",
    "xdrlib": "Removed in Python 3.13; legacy XDR data parser",
    # Python 3.12 removals
    "imp": "Removed in Python 3.12; use importlib",
    "distutils": "Removed in Python 3.12; use setuptools or packaging",
    "pkg_resources": "Deprecated legacy packaging; use importlib.resources / importlib.metadata",
    # Older removals
    "time.clock": "Removed in Python 3.8; use time.perf_counter() or time.process_time()",
}

class ArchaeologyScanner(ast.NodeVisitor):
    """AST visitor detecting obsolete modules and broken APIs."""

    def __init__(self, filename: str):
        self.filename = filename
        self.findings: List[Dict[str, Any]] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            base_mod = alias.name.split(".")[0]
            if alias.name in KNOWN_DEPRECATIONS:
                self.findings.append({
                    "line": node.lineno,
                    "target": alias.name,
                    "reason": KNOWN_DEPRECATIONS[alias.name],
                    "type": "deprecated_module"
                })
            elif base_mod in KNOWN_DEPRECATIONS:
                self.findings.append({
                    "line": node.lineno,
                    "target": alias.name,
                    "reason": KNOWN_DEPRECATIONS[base_mod],
                    "type": "deprecated_module"
                })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            base_mod = node.module.split(".")[0]
            if node.module in KNOWN_DEPRECATIONS:
                self.findings.append({
                    "line": node.lineno,
                    "target": node.module,
                    "reason": KNOWN_DEPRECATIONS[node.module],
                    "type": "deprecated_module"
                })
            elif base_mod in KNOWN_DEPRECATIONS:
                self.findings.append({
                    "line": node.lineno,
                    "target": node.module,
                    "reason": KNOWN_DEPRECATIONS[base_mod],
                    "type": "deprecated_module"
                })
            for alias in node.names:
                full_name = f"{node.module}.{alias.name}"
                if full_name in KNOWN_DEPRECATIONS:
                    self.findings.append({
                        "line": node.lineno,
                        "target": full_name,
                        "reason": KNOWN_DEPRECATIONS[full_name],
                        "type": "deprecated_api"
                    })
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name):
            full_attr = f"{node.value.id}.{node.attr}"
            if full_attr in KNOWN_DEPRECATIONS:
                self.findings.append({
                    "line": node.lineno,
                    "target": full_attr,
                    "reason": KNOWN_DEPRECATIONS[full_attr],
                    "type": "deprecated_api"
                })
        self.generic_visit(node)

def inspect_file(filepath: Union[str, Path]) -> List[Dict[str, Any]]:
    """Scan a single Python file for bitrot, deprecated modules, and syntax errors."""
    path = Path(filepath)
    with trace_span("necrogit.archaeology", f"inspect_{path.name}"):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                code_content = f.read()
            tree = ast.parse(code_content, filename=str(path))
            scanner = ArchaeologyScanner(str(path))
            scanner.visit(tree)
            return scanner.findings
        except SyntaxError as e:
            return [{
                "line": e.lineno or 1,
                "target": "SyntaxError",
                "reason": f"File fails AST parsing: {e.msg}",
                "type": "syntax_rot"
            }]
        except Exception as e:
            return [{
                "line": 1,
                "target": "ArchaeologyError",
                "reason": f"Inspection error: {str(e)}",
                "type": "archaeology_failure"
            }]

def inspect_directory(target_dir: Union[str, Path]) -> Dict[str, List[Dict[str, Any]]]:
    """Recursively inspect a directory of Python files for bitrot artifacts."""
    path = Path(target_dir)
    report: Dict[str, List[Dict[str, Any]]] = {}
    ignored_patterns = {".git", "venv", ".venv", "__pycache__", ".pytest_cache", "build", "dist", ".egg-info"}

    for py_file in path.rglob("*.py"):
        if any(ignored in py_file.parts for ignored in ignored_patterns):
            continue
        issues = inspect_file(py_file)
        if issues:
            report[str(py_file.relative_to(path))] = issues
    return report
