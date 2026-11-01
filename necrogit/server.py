import http.server
import socketserver
import webbrowser
from pathlib import Path
from rich.console import Console

console = Console(legacy_windows=False)

class WebAssetHandler(http.server.SimpleHTTPRequestHandler):
    """Quiet static file handler serving the embedded NecroGit CRT web workbench."""

    def __init__(self, *args, **kwargs):
        web_dir = Path(__file__).parent / "web"
        super().__init__(*args, directory=str(web_dir), **kwargs)

    def log_message(self, format, *args):
        # Quiet default logging to keep terminal focused
        pass

def run_local_server(port: int = 8000, auto_open: bool = True) -> None:
    """Launch local HTTP server to host the embedded retro CRT playground & docs."""
    web_dir = Path(__file__).parent / "web"
    if not (web_dir / "index.html").exists():
        console.print("[red]Error: Web assets not found in package.[/red]")
        return

    url = f"http://localhost:{port}"
    console.print(f"[bold magenta]🕯️  Manifesting NecroGit Terminal Séance on {url}[/bold magenta]")
    console.print("[dim]Press Ctrl+C to sever the spectral connection.[/dim]")

    if auto_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    # Allow immediate socket reuse
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), WebAssetHandler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                console.print("\n[yellow]Séance portal closed.[/yellow]")
    except OSError as e:
        console.print(f"[red]Port {port} in use or unavailable: {e}[/red]")
