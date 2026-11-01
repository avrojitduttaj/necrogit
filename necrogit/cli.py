import sys
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

    if not persona["is_git"]:
        console.print("[red]No git presence detected in this directory.[/red]")
        return

    set_agent_context("maintainer_persona", persona)

    # Persist séance dossier to Backboard / local storage
    memory = BackboardMemory()
    repo_name = Path(repo_path).resolve().name
    memory.save_dossier(repo_name, persona, relics_count=0, last_action="summon")

    sample_logs = "\n".join(f"  • {msg}" for msg in persona["sample_logs"]) if persona["sample_logs"] else "  • (No recent commit messages recorded)"
    output = (
        f"[bold cyan]Dominant Spirit:[/bold cyan] {persona['maintainer']}\n"
        f"[bold cyan]Last Walked the Earth:[/bold cyan] {persona['last_active']}\n"
        f"[bold cyan]Total Invocations:[/bold cyan] {persona['commit_count']} commits\n"
        f"[bold cyan]Persona Temperament:[/bold cyan] {persona['brevity']}\n\n"
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
@click.option("--apply", is_flag=True, help="Apply proposed diff directly to file")
def patch(file_path: str, repo: str, model: str, apply: bool) -> None:
    """Channel the maintainer to draft an in-style resurrective patch."""
    target = Path(file_path)
    if not target.exists():
        console.print(f"[red]Cannot find target artifact: {file_path}[/red]")
        return

    record_breadcrumb("cli", "Invoking patch command", data={"target": file_path, "model": model})

    medium = MaintainerMedium(repo)
    persona = medium.summon_maintainer_essence()
    engine = SeanceEngine(model=model)

    issues = inspect_file(target)
    context_str = "\n".join([f"- Line {i['line']}: {i['target']} ({i['reason']})" for i in issues]) if issues else "General modernization and syntax cleanup."

    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        code_body = f.read()

    with console.status(f"[bold red]Consulting {persona['maintainer']} via {model}...[/bold red]"):
        diff = engine.consult_ghost(persona, code_body, context_str)

    console.print(Panel(diff, title=f"[green]Ethereal Unified Diff: {file_path}[/green]"))

    if apply:
        console.print("[yellow]Applying patch directly...[/yellow]")
        patch_file = target.with_suffix(".patch")
        patch_file.write_text(diff, encoding="utf-8")
        console.print(f"[green]Diff saved to {patch_file}. Run `git apply {patch_file}` to commit.[/green]")

    # Persist update to memory
    memory = BackboardMemory()
    repo_name = Path(repo).resolve().name
    memory.save_dossier(repo_name, persona, relics_count=len(issues), last_action=f"patch {target.name}")

@cli.command()
@click.argument("file_path")
@click.option("--symbol", default=None, help="Specific function, class, or variable name to analyze")
@click.option("--repo", default=".", help="Root path of the repository")
@click.option("--model", default="gemma2:9b", help="Local open-weight model tag")
def explain(file_path: str, symbol: Optional[str], repo: str, model: str) -> None:
    """Channel the maintainer to explain obscure historical design choices and legacy architecture."""
    target = Path(file_path)
    if not target.exists():
        console.print(f"[red]Cannot find target artifact: {file_path}[/red]")
        return

    record_breadcrumb("cli", "Invoking explain command", data={"target": file_path, "symbol": symbol, "model": model})

    medium = MaintainerMedium(repo)
    persona = medium.summon_maintainer_essence()
    engine = SeanceEngine(model=model)

    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        code_body = f.read()

    target_desc = f"{target.name}:{symbol}" if symbol else target.name
    with console.status(f"[bold cyan]Channeling {persona['maintainer']}'s memories of {target_desc} via {model}...[/bold cyan]"):
        explanation = engine.explain_design(persona, code_body, symbol_query=symbol)

    console.print(Panel(explanation, title=f"[cyan]Historical Design Exegesis: {target_desc}[/cyan]", border_style="cyan"))

@cli.command()
def memory() -> None:
    """Inspect persistent repository dossiers and Backboard memory synchronization status."""
    mem = BackboardMemory()
    dossiers = mem.list_dossiers()

    status_str = "[green]Connected[/green]" if mem.api_key else "[yellow]Air-Gapped / Local Mode (.necrogit/seance_memory.json)[/yellow]"
    console.print(f"[bold magenta]🧠 Backboard Persistent Memory:[/bold magenta] {status_str}")

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

if __name__ == "__main__":
    cli()
