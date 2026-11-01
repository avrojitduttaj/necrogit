import sys
from pathlib import Path
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
from necrogit.core.engine import SeanceEngine
from necrogit.telemetry import init_telemetry

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
    medium = MaintainerMedium(repo_path)
    persona = medium.summon_maintainer_essence()

    if not persona["is_git"]:
        console.print("[red]No git presence detected in this directory.[/red]")
        return

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
    report = inspect_directory(target_dir)

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
@click.option("--model", default="gemma2:9b", help="Local open-weight model tag")
@click.option("--apply", is_flag=True, help="Apply proposed diff directly to file")
def patch(file_path: str, repo: str, model: str, apply: bool) -> None:
    """Channel the maintainer to draft an in-style resurrective patch."""
    target = Path(file_path)
    if not target.exists():
        console.print(f"[red]Cannot find target artifact: {file_path}[/red]")
        return

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

if __name__ == "__main__":
    cli()
