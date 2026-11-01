#!/usr/bin/env python3
"""NecroGit Interactive Séance Demonstration."""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from necrogit.core.archaeology import inspect_file
from necrogit.core.persona import MaintainerMedium

console = Console()

def run_demo():
    console.print(Panel.fit("🕯️  [bold magenta]NecroGit Live Séance Walkthrough[/bold magenta] 🕯️", border_style="magenta"))

    relic_path = Path(__file__).parent / "ancient_relic.py"
    console.print(f"\n[cyan]1. Performing Code Archaeology on [bold]{relic_path.name}[/bold]...[/cyan]")
    findings = inspect_file(relic_path)

    for item in findings:
        console.print(f"  [red]• Line {item['line']}:[/red] [yellow]{item['target']}[/yellow] — [white]{item['reason']}[/white]")

    console.print("\n[cyan]2. Divining Maintainer Persona from current workspace...[/cyan]")
    medium = MaintainerMedium(str(Path(__file__).parent.parent))
    persona = medium.summon_maintainer_essence()

    console.print(f"  Spirit Name: [bold green]{persona['maintainer']}[/bold green]")
    console.print(f"  Temperament: [bold cyan]{persona['brevity']}[/bold cyan]")
    console.print(f"  Last Walked: [bold yellow]{persona['last_active']}[/bold yellow]")

    console.print("\n[dim]Run `necrogit inspect demo/` or `necrogit patch demo/ancient_relic.py` to channel the ghost live.[/dim]\n")

if __name__ == "__main__":
    run_demo()
