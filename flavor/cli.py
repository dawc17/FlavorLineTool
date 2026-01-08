# flavor/cli.py
import typer
from rich.console import Console
from flavor.config import get_cookie_count, set_cookie_count

app = typer.Typer()
cookies_app = typer.Typer()
app.add_typer(cookies_app, name="cookies", help="Manage your cookie stash.")

console = Console()

@app.callback()
def callback():
    """
    FlavorLineTool - A CLI for tracking cookies and interacting with Flavortown.
    """
    
@app.command()
def status():
    """Check FLT's status (if for some reason you feel you have to)."""
    console.print("FlavorLineTool is alive, I think!!!", style="blink green")

@cookies_app.command("add")
def cookies_add(number: int):
    """Add cookies to your stash."""
    current = get_cookie_count()
    new_count = current + number
    set_cookie_count(new_count)
    console.print(f"Added {number} cookies. Total: {new_count}", style="green")

@cookies_app.command("remove")
def cookies_remove(number: int):
    """Remove cookies from your stash."""
    current = get_cookie_count()
    new_count = current - number
    if new_count < 0:
        console.print("You can't have negative cookies! Setting to 0.", style="yellow")
        new_count = 0
    set_cookie_count(new_count)
    console.print(f"Removed {number} cookies. Total: {new_count}", style="green")

@cookies_app.command("set")
def cookies_set(number: int):
    """Set the exact number of cookies in your stash."""
    if number < 0:
        console.print("You can't set negative cookies.", style="red")
        raise typer.Exit(code=1)
    set_cookie_count(number)
    console.print(f"Cookie count set to {number}.", style="green")

@cookies_app.command("show")
def cookies_show():
    """Print your current amount of cookies."""
    current = get_cookie_count()
    console.print(f"You currently have {current} cookies.", style="green")

def main():
    app()

if __name__ == "__main__":
    main()
