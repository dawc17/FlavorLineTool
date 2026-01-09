import typer
from rich.console import Console
from flavor.config import get_flavor_id
from flavor.api import get_user_by_id, APIError

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command("show")
def show():
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
