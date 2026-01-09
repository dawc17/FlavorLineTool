import typer
from rich.console import Console
from flavor.hackatime import get_time_today, HackatimeAPIError

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command("today")
def today():
    """Show how much you've coded today."""
    try:
        with console.status("Fetching your coding time...", spinner="dots"):
            data = get_time_today()
        
        grand_total = data.get("data", {}).get("grand_total", {})
        text = grand_total.get("text", "0 secs")
        
        console.print(f"You have coded for [bold cyan]{text}[/bold cyan] today!", style="green")
        
    except HackatimeAPIError as e:
        console.print(f"Error: {e}", style="bold red")
