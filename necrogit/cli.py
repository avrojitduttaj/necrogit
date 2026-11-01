import sys
import shutil
import zipfile
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Ensure Windows consoles don't crash on emojis in docstrings / help output
if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from necrogit.core.persona import MaintainerMedium
from necrogit.core.archaeology import inspect_directory, inspect_file
from necrogit.core.engine import SeanceEngine, SUPPORTED_MODELS
from necrogit.core.backboard import BackboardMemory
from necrogit.telemetry import init_telemetry, record_breadcrumb, set_agent_context

console = Console(legacy_windows=False)
init_telemetry()

@click.group()
def cli() -> None:
    """🕯️ NecroGit: The Repository Medium. Commune with dead code and resurrect bitrot."""
    pass

@cli.command()
@click.argument("repo_path", default=".")
def summon(repo_path: str) -> None:
    """Summon and interview the maintainer's spirit from Git history."""
    console.print("[magenta]🕯️  Casting circle and reading repository runes...[/magenta]")
    record_breadcrumb("cli", "Invoking summon command", data={"repo_path": repo_path})

    medium = MaintainerMedium(repo_path)
    persona = medium.summon_maintainer_essence()

    if not persona.get("is_git"):
        console.print("[red]No git presence detected in this directory.[/red]")
        return

    set_agent_context("maintainer_persona", persona)

    # Persist séance dossier to Backboard / local storage
    memory_store = BackboardMemory()
    repo_name = Path(repo_path).resolve().name
    memory_store.save_dossier(repo_name, persona, relics_count=0, last_action="summon")

    sample_logs = "\n".join(f"  • {msg}" for msg in persona.get("sample_logs", [])) if persona.get("sample_logs") else "  • (No recent commit messages recorded)"
    output = (
        f"[bold cyan]Dominant Spirit:[/bold cyan] {persona.get('maintainer', 'Unknown')}\n"
        f"[bold cyan]Last Walked the Earth:[/bold cyan] {persona.get('last_active', 'Unknown')}\n"
        f"[bold cyan]Total Invocations:[/bold cyan] {persona.get('commit_count', 0)} commits\n"
        f"[bold cyan]Persona Temperament:[/bold cyan] {persona.get('brevity', 'balanced')}\n\n"
        f"[bold yellow]Sample Historical Invocations:[/bold yellow]\n"
        f"{sample_logs}"
    )
    console.print(Panel(output, title="[bold red]Séance Manifestation[/bold red]", border_style="dim"))

@cli.command()
@click.argument("target_dir", default=".")
def inspect(target_dir: str) -> None:
    """Scan local code files for bitrot, deprecated modules, and breaking syntax."""
    console.print(f"[dim]Performing code archaeology on: {target_dir}...[/dim]")
    record_breadcrumb("cli", "Invoking inspect command", data={"target_dir": target_dir})

    report = inspect_directory(target_dir)
    total_issues = sum(len(issues) for issues in report.values())
    record_breadcrumb("archaeology", f"Scan complete. Discovered {total_issues} relics.", data={"files_with_rot": len(report)})

    if not report:
        console.print("[green]✨ No immediate bitrot relics or deprecated imports identified.[/green]")
        return

    table = Table(title="🪦 Identified Bitrot Relics", border_style="red")
    table.add_column("File", style="cyan")
    table.add_column("Line", style="magenta")
    table.add_column("Artifact", style="yellow")
    table.add_column("Historical Diagnosis", style="white")

    for file_rel, issues in report.items():
        for issue in issues:
            table.add_row(file_rel, str(issue["line"]), issue["target"], issue["reason"])

    console.print(table)

@cli.command()
@click.argument("file_path")
@click.option("--repo", default=".", help="Root path of the repository")
@click.option("--model", default="gemma2:9b", help="Local open-weight model tag (e.g. gemma2:9b, llama3.2:3b)")
@click.option("--base-url", default=None, help="Inference API endpoint (default: http://localhost:11434/v1)")
@click.option("--apply", is_flag=True, help="Apply proposed diff directly to file")
def patch(file_path: str, repo: str, model: str, base_url: Optional[str], apply: bool) -> None:
    """Channel the maintainer to draft an in-style resurrective patch."""
    target = Path(file_path)
    if not target.exists():
        console.print(f"[red]Cannot find target artifact: {file_path}[/red]")
        return

    record_breadcrumb("cli", "Invoking patch command", data={"target": file_path, "model": model})

    medium = MaintainerMedium(repo)
    persona = medium.summon_maintainer_essence()
    engine = SeanceEngine(base_url=base_url, model=model)

    issues = inspect_file(target)
    context_str = "\n".join([f"- Line {i['line']}: {i['target']} ({i['reason']})" for i in issues]) if issues else "General modernization and syntax cleanup."

    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        code_body = f.read()

    with console.status(f"[bold red]Consulting {persona.get('maintainer', 'maintainer')} via {model}...[/bold red]"):
        diff = engine.consult_ghost(persona, code_body, context_str)

    if diff.startswith("💀 ["):
        console.print(Panel(diff, title=f"[red]Séance Interrupted: {file_path}[/red]", border_style="red"))
        return

    console.print(Panel(diff, title=f"[green]Ethereal Unified Diff: {file_path}[/green]"))

    if apply:
        patch_file = target.with_suffix(".patch")
        patch_file.write_text(diff, encoding="utf-8")
        console.print(f"[green]Diff saved to {patch_file}. Run `git apply {patch_file}` to commit.[/green]")

    # Persist update to memory
    memory_store = BackboardMemory()
    repo_name = Path(repo).resolve().name
    memory_store.save_dossier(repo_name, persona, relics_count=len(issues), last_action=f"patch {target.name}")

@cli.command()
@click.argument("file_path")
@click.option("--symbol", default=None, help="Specific function, class, or variable name to analyze")
@click.option("--repo", default=".", help="Root path of the repository")
@click.option("--model", default="gemma2:9b", help="Local open-weight model tag")
@click.option("--base-url", default=None, help="Inference API endpoint (default: http://localhost:11434/v1)")
def explain(file_path: str, symbol: Optional[str], repo: str, model: str, base_url: Optional[str]) -> None:
    """Channel the maintainer to explain obscure historical design choices and legacy architecture."""
    target = Path(file_path)
    if not target.exists():
        console.print(f"[red]Cannot find target artifact: {file_path}[/red]")
        return

    record_breadcrumb("cli", "Invoking explain command", data={"target": file_path, "symbol": symbol, "model": model})

    medium = MaintainerMedium(repo)
    persona = medium.summon_maintainer_essence()
    engine = SeanceEngine(base_url=base_url, model=model)

    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        code_body = f.read()

    target_desc = f"{target.name}:{symbol}" if symbol else target.name
    with console.status(f"[bold cyan]Channeling {persona.get('maintainer', 'maintainer')}'s memories of {target_desc} via {model}...[/bold cyan]"):
        explanation = engine.explain_design(persona, code_body, symbol_query=symbol)

    if explanation.startswith("💀 ["):
        console.print(Panel(explanation, title=f"[red]Séance Interrupted: {target_desc}[/red]", border_style="red"))
        return

    console.print(Panel(explanation, title=f"[cyan]Historical Design Exegesis: {target_desc}[/cyan]", border_style="cyan"))

@cli.command()
@click.argument("repo_path", required=False, default=None)
@click.option("--clear", is_flag=True, help="Clear stored dossiers from persistent memory.")
def memory(repo_path: Optional[str] = None, clear: bool = False) -> None:
    """Inspect persistent repository dossiers and Backboard memory synchronization status."""
    mem = BackboardMemory()

    if clear:
        mem.clear()
        console.print("[yellow]Séance memory cleared.[/yellow]")
        return

    status_str = "[green]Connected[/green]" if mem.api_key else "[yellow]Air-Gapped / Local Mode (.necrogit/seance_memory.json)[/yellow]"
    console.print(f"[bold magenta]🧠 Backboard Persistent Memory:[/bold magenta] {status_str}")

    dossiers = mem.list_dossiers()
    if repo_path:
        repo_key = Path(repo_path).resolve().name
        dossier = mem.get_dossier(repo_key)
        if not dossier:
            console.print(f"[dim]No séance dossier found for repository '{repo_key}'.[/dim]")
            return
        dossiers = {repo_key: dossier}

    if not dossiers:
        console.print("[dim]No repository dossiers recorded in persistent memory yet. Run `necrogit summon` or `necrogit patch`.[/dim]")
        return

    table = Table(title="📜 Known Repository Dossiers", border_style="magenta")
    table.add_column("Repository", style="cyan")
    table.add_column("Maintainer Spirit", style="yellow")
    table.add_column("Temperament", style="green")
    table.add_column("Relics", style="red")
    table.add_column("Last Action", style="white")

    for repo_key, info in dossiers.items():
        table.add_row(
            repo_key,
            str(info.get("maintainer", "Unknown")),
            str(info.get("temperament", "laconic")),
            str(info.get("relics_count", 0)),
            str(info.get("last_action", "none")),
        )

    console.print(table)

@cli.command()
@click.option("--port", default=8000, help="Local port to serve the web terminal.")
@click.option("--open/--no-open", "auto_open", default=True, help="Automatically open browser.")
def serve(port: int, auto_open: bool) -> None:
    """Launch the interactive web terminal & documentation in your browser."""
    from necrogit.server import run_local_server
    run_local_server(port=port, auto_open=auto_open)

@cli.command("export-web")
@click.argument("destination", default="./necrogit-web")
@click.option("--zip/--no-zip", "create_zip", default=True, help="Create a downloadable ZIP archive of the site.")
def export_web(destination: str, create_zip: bool) -> None:
    """Export the standalone HTML/JS documentation workbench for hosting or external inspection."""
    src_dir = Path(__file__).parent / "web"
    dest_path = Path(destination).resolve()

    dest_path.mkdir(parents=True, exist_ok=True)
    count = 0
    copied_files = []

    for item in src_dir.glob("*"):
        if item.is_file() and not item.name.endswith(".py"):
            target_item = dest_path / item.name
            shutil.copy2(item, target_item)
            copied_files.append(target_item)
            count += 1

    # Include helpful preview README
    readme_path = dest_path / "README.md"
    readme_path.write_text(
        "# 🕯️ NecroGit Web Documentation Workbench\n\n"
        "This directory contains the self-contained static web interface for NecroGit.\n\n"
        "### How to Preview Locally:\n"
        "```bash\n"
        "python -m http.server 8080\n"
        "```\n"
        "Then open `http://localhost:8080` in your browser.\n",
        encoding="utf-8"
    )
    copied_files.append(readme_path)
    count += 1

    # Create downloadable ZIP archive
    zip_path = None
    if create_zip:
        zip_path = dest_path / "necrogit-site.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in copied_files:
                if f != zip_path:
                    zipf.write(f, arcname=f.name)

    console.print(f"[bold green]✨ Exported NecroGit web assets ({count} files) to: [cyan]{dest_path}[/cyan][/bold green]")
    console.print(f"[dim]To view: cd \"{dest_path}\" && python -m http.server 8080[/dim]")
    if zip_path:
        console.print(f"[dim]Downloadable bundle created at: [cyan]{zip_path}[/cyan][/dim]")

@cli.command()
@click.option("--model", default="gemma2:9b", help="Model to verify against local Ollama")
@click.option("--base-url", default=None, help="Inference API endpoint (default: http://localhost:11434/v1)")
def doctor(model: str, base_url: Optional[str]) -> None:
    """Inspect installation integrity, Git availability, and local AI model connectivity."""
    console.print(Panel.fit("🩺 [bold cyan]NecroGit System Diagnostics[/bold cyan]", border_style="cyan"))

    # 1. Python version check
    py_ver = sys.version.split()[0]
    py_ok = sys.version_info >= (3, 10)
    py_status = "[green]OK[/green]" if py_ok else "[red]FAIL (Requires Python >= 3.10)[/red]"
    console.print(f"• Python Environment: {py_ver} ({py_status})")

    # 2. Git status
    try:
        import git
        repo = git.Repo(".", search_parent_directories=True)
        git_status = f"[green]OK (Git {git.__version__}, repo: {Path(repo.working_dir).name})[/green]"
    except Exception as e:
        git_status = f"[yellow]WARNING: Not a git repo or GitPython error ({e})[/yellow]"
    console.print(f"• Git Telemetry: {git_status}")

    # 3. Web Assets
    web_dir = Path(__file__).parent / "web"
    web_ok = (web_dir / "index.html").exists()
    web_status = "[green]OK (Found web/index.html)[/green]" if web_ok else "[red]FAIL (web/index.html missing)[/red]"
    console.print(f"• Web Documentation Package: {web_status}")

    # 4. Sentry Telemetry
    from necrogit.telemetry import _is_sentry_active
    sentry_status = "[green]ACTIVE[/green]" if _is_sentry_active() else "[dim]INACTIVE (SENTRY_DSN not set - running fully private)[/dim]"
    console.print(f"• Sentry Agent Tracing: {sentry_status}")

    # 5. Backboard Memory
    mem = BackboardMemory()
    backboard_status = "[green]CONNECTED[/green]" if mem.api_key else "[yellow]AIR-GAPPED (Local .necrogit/seance_memory.json)[/yellow]"
    console.print(f"• Backboard Persistent Memory: {backboard_status}")

    # 6. Local LLM Server Check
    engine = SeanceEngine(base_url=base_url, model=model)
    console.print(f"• Probing Local LLM ({engine.base_url}, target model: {model})...")
    health = engine.check_health()
    if health.get("connected"):
        model_status = "[green]READY[/green]" if health.get("model_found") else f"[yellow]NOT FOUND (Run: `ollama pull {model}`)[/yellow]"
        console.print(f"  └─ Server: [green]ONLINE[/green] ({health.get('endpoint')})")
        console.print(f"  └─ Model Status: {model_status}")
        available = ", ".join(health.get("available_models", [])) or "none"
        console.print(f"  └─ Installed Models: [dim]{available}[/dim]")
    else:
        console.print(f"  └─ Server: [red]OFFLINE[/red] ({health.get('error', 'Cannot connect')})")
        console.print("  └─ Action: Start Ollama with `ollama serve` or run `ollama run gemma2:9b`")

@cli.command("clone-demo")
@click.argument("destination", default="./necrogit-demo-sandbox")
def clone_demo(destination: str) -> None:
    """Clone standalone test relics into an external workspace or VS Code folder."""
    dest_path = Path(destination).resolve()
    dest_path.mkdir(parents=True, exist_ok=True)

    relic_content = '''"""Legacy utility script with removed Python stdlib calls."""
import imp
import pipes
import time

def process_archived_stream(command_str):
    t_start = time.clock()
    safe_target = pipes.quote(command_str)
    handle = imp.find_module("sys")
    return t_start, safe_target, handle
'''
    target_file = dest_path / "legacy_relic.py"
    target_file.write_text(relic_content, encoding="utf-8")

    console.print(f"[bold green]✨ Cloned demo relic to: [cyan]{target_file}[/cyan][/bold green]")
    console.print(f"[dim]Run: necrogit inspect {destination}[/dim]")

if __name__ == "__main__":
    cli()
