# flavor/cli.py
import typer
from rich.console import Console
from rich.table import Table
from flavor.config import set_api_key, set_flavor_id, get_flavor_id
from flavor.api import get_users, get_user_by_id, APIError, get_shop

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
def loginapi(key: str):
    """Login with your Flavortown API key."""
    if not key.startswith("ft_sk_"):
        console.print("Invalid API key format. It must start with 'ft_sk_'.", style="bold red")
        raise typer.Exit(code=1)
    
    set_api_key(key)
    console.print(f"Successfully logged in with to Flavortown API!", style="green")

@app.command()
def loginid(key: str):
    """Login with your Flavortown UserID."""
    set_flavor_id(key)
    console.print(f"Successfully logged in with the Flavortown User ID!", style="green")


@cookies_app.command("show")
def cookies_show():
    """Print your current amount of cookies from the Flavortown API."""
    flavor_id = get_flavor_id()
    if not flavor_id:
        console.print("You must login with your Flavor ID first using 'flavor loginid <id>'", style="bold red")
        raise typer.Exit(code=1)
    
    try:
        with console.status("Fetching your cookies from API...", spinner="dots"):
            data = get_user_by_id(int(flavor_id))
            name = data.get("display_name")
        
        cookie_count = data.get("cookies")
        if cookie_count is None:
            cookie_count = 0
            
        console.print(f"You ({name}) have [bold yellow]{cookie_count}[/bold yellow] cookies.", style="green")
        
    except APIError as e:
        console.print(f"Error: {e}", style="bold red")
    except ValueError:
        console.print("Stored Flavor ID is not a valid integer.", style="bold red")

@list_app.command("shop")
def list_shop():
    """List all items in the shop."""
    try:
        with console.status("Fetching shop items...", spinner="dots"):
            items = get_shop()
        
        if not items:
            console.print("No items found in the shop.", style="yellow")
            return

        items.sort(key=lambda x: x.get("id", 0))

        table = Table(title="Flavortown Shop")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Cost", justify="right", style="green")
        table.add_column("Stock", justify="right", style="yellow")
        table.add_column("Limited", justify="center", style="red")

        for item in items:
            i_id = str(item.get("id"))
            name = item.get("name") or "Unknown"
            
            ticket_cost = item.get("ticket_cost", {})
            cost = str(ticket_cost.get("base_cost") if ticket_cost else "N/A")

            stock = str(item.get("stock")) if item.get("stock") is not None else "∞"
            
            is_limited = "Yes" if item.get("limited") else "No"
            table.add_row(i_id, name, cost, stock, is_limited)
        
        console.print(table)
    except APIError as e:
        console.print(f"Error: {e}", style="bold red")

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
