import typer
from rich.console import Console
from rich.table import Table
from flavor.config import set_flavor_id, get_flavor_id, set_hackatime_username, get_hackatime_username
from flavor.api import get_user_by_id, APIError
from flavor.hackatime import get_stats, HackatimeAPIError

# Command modules
from flavor.commands.cookies import app as cookies_app
from flavor.commands.lists import app as list_app
from flavor.commands.times import app as time_app
from flavor.commands.login import app as login_app
from flavor.commands.search import app as search_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(cookies_app, name="cookies", help="Manage your cookie stash.")
app.add_typer(list_app, name="list", help="List resources from Flavortown.")
app.add_typer(time_app, name="time", help="Track your coding time with Hackatime.")
app.add_typer(login_app, name="login", help="Manage your login credentials.")
app.add_typer(search_app, name="search", help="Search for resources.")

console = Console()

@app.callback()
def callback():
    """
    FlavorLineTool - A CLI for tracking cookies and interacting with Flavortown.
    """
    pass
    
@app.command()
def status():
    """Check FLT's status (if for some reason you feel you have to)."""
    console.print("FlavorLineTool is alive, I think!!!", style="blink green")

@app.command()
def stats():
    """Show all your stats (Flavortown + Hackatime)."""
    flavor_id = get_flavor_id()
    if not flavor_id:
        console.print("You are not logged in with your Flavor ID.", style="yellow")
        flavor_id = typer.prompt("Please enter your Flavortown User ID")
        set_flavor_id(flavor_id)
        console.print(f"Flavor ID saved!", style="green")

    try:
        with console.status("Fetching your stats...", spinner="dots"):
            ft_data = get_user_by_id(int(flavor_id))
            
            # Fetch Hackatime data
            ht_username = get_hackatime_username()
            
        if not ht_username:
            console.print("You have not set your Hackatime username.", style="yellow")
            ht_username = typer.prompt("Please enter your Hackatime username")
            set_hackatime_username(ht_username)
            console.print(f"Hackatime username saved!", style="green")

        with console.status("Fetching Hackatime stats...", spinner="dots"):
           ht_data = get_stats(ht_username)

        display_name = ft_data.get("display_name") or "Unknown"
        cookies = ft_data.get("cookies")
        if cookies is None:
            cookies = 0

        ht_data_content = ht_data.get("data", {})
        time_str = ht_data_content.get("human_readable_total", "0 secs")
        
        languages = ht_data_content.get("languages", [])
        top_lang = "N/A"
        top_lang_time = "N/A"
        
        if languages:
            first_lang = languages[0]
            top_lang = first_lang.get("name", "Unknown")
            top_lang_time = first_lang.get("text", "0 secs")

        table = Table(title="Your Stats")
        table.add_column("Display Name", style="magenta")
        table.add_column("Total Time Coded", style="cyan")
        table.add_column("Cookies", justify="right", style="yellow")
        table.add_column("Top Language", style="blue")
        table.add_column("Time in Top Language", style="green")
        
        table.add_row(display_name, time_str, str(cookies), top_lang, top_lang_time)
        
        console.print(table)

    except APIError as e:
        console.print(f"API Error: {e}", style="bold red")
    except HackatimeAPIError as e:
        console.print(f"Hackatime Error: {e}", style="bold red")
    except ValueError:
        console.print("Stored Flavor ID is not a valid integer.", style="bold red")


def main():
    app()

if __name__ == "__main__":
    main()
