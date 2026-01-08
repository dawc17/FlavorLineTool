# flavor/cli.py
import typer
from rich.console import Console
from rich.table import Table
from flavor.config import set_api_key, set_slack_id
from flavor.api import get_users, APIError

app = typer.Typer()
cookies_app = typer.Typer()
list_app = typer.Typer()

app.add_typer(cookies_app, name="cookies", help="Manage your cookie stash.")
app.add_typer(list_app, name="list", help="List resources from Flavortown.")

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

@app.command()
def loginflavor(key: str):
    """Login with your Flavortown API key."""
    if not key.startswith("ft_sk_"):
        console.print("Invalid API key format. It must start with 'ft_sk_'.", style="bold red")
        raise typer.Exit(code=1)
    
    set_api_key(key)
    console.print(f"Successfully logged in with to Flavortown API!", style="green")

@app.command()
def loginslack(key: str):
    """Login with your Slack UserID."""
    set_slack_id(key)
    console.print(f"Successfully logged in with the Slack User ID!", style="green")


@cookies_app.command("show")
def cookies_show():
    """Print your current amount of cookies."""
    current = get_cookie_count()
    console.print(f"You currently have {current} cookies.", style="green")

@list_app.command("users")
def list_users():
    """List all users."""
    try:
        with console.status("Fetching users...", spinner="dots"):
            data = get_users()
        users = data.get("users", [])
        
        if not users:
            console.print("No users found.", style="yellow")
            return

        table = Table(title="Flavortown Users")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="magenta")
        table.add_column("Slack ID", style="green")
        table.add_column("Cookies", justify="right", style="yellow")

        for user in users:
            # Handle possible None values for display_name or others
            d_name = user.get("display_name") or "Unknown"
            s_id = user.get("slack_id") or "N/A"
            c_count = str(user.get("cookies") if user.get("cookies") is not None else 0)
            
            table.add_row(str(user.get("id")), d_name, s_id, c_count)
        
        console.print(table)
    except APIError as e:
        console.print(f"Error: {e}", style="bold red")

def main():
    app()

if __name__ == "__main__":
    main()
