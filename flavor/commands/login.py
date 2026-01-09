import typer
from rich.console import Console
from flavor.config import set_api_key, set_flavor_id, set_hackatime_key, set_hackatime_username

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command("api")
def api(key: str = typer.Argument(None, help="Your Flavortown API key")):
    """Login with your Flavortown API key."""
    if key is None:
        key = typer.prompt("Please enter your Flavortown API key", hide_input=True)

    if not key.startswith("ft_sk_"):
        console.print("Invalid API key format. It must start with 'ft_sk_'.", style="bold red")
        raise typer.Exit(code=1)
    
    set_api_key(key)
    console.print(f"Successfully logged in with to Flavortown API!", style="green")

@app.command("id")
def id(key: str = typer.Argument(None, help="Your Flavortown User ID")):
    """Login with your Flavortown UserID."""
    if key is None:
        key = typer.prompt("Please enter your Flavortown User ID")

    set_flavor_id(key)
    console.print(f"Successfully logged in with the Flavortown User ID!", style="green")

@app.command("hackatime")
def hackatime(key: str = typer.Argument(None, help="Your Hackatime API key")):
    """Login with your Hackatime API key."""
    if key is None:
        key = typer.prompt("Please enter your Hackatime API key", hide_input=True)

    set_hackatime_key(key)
    console.print(f"Successfully logged in with Hackatime API key!", style="green")

@app.command("hackatimeuser")
def hackatimeuser(username: str = typer.Argument(None, help="Your Hackatime username")):
    """Set your Hackatime username."""
    if username is None:
        username = typer.prompt("Please enter your Hackatime username")

    set_hackatime_username(username)
    console.print(f"Successfully set Hackatime username to {username}!", style="green")
