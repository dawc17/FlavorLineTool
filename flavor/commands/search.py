import typer
from rich.console import Console
from rich.table import Table
from flavor.api import get_users, APIError

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.callback()
def callback():
    """
    Search - specific resources.
    """
    pass

@app.command("users")
def search_users(query: str, page: int = 1):
    """Search for users by display name or Slack ID."""
    try:
        with console.status(f"Searching for '{query}' (page {page})...", spinner="dots"):
            data = get_users(page=page, query=query)
        
        users_list = data.get("users", [])
        
        if not users_list:
            console.print(f"No users found matching '{query}'.", style="yellow")
            return

        pagination = data.get("pagination", {})
        total_users = pagination.get("total_count", "Unknown")
        current_page = pagination.get("current_page", page)
        total_pages = pagination.get("total_pages", "Unknown")
        
        title = f"Search Results for '{query}'"
        table = Table(title=title)
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="magenta")
        table.add_column("Slack ID", style="green")
        table.add_column("Cookies", justify="right", style="yellow")

        for user in users_list:
            d_name = user.get("display_name") or "Unknown"
            s_id = user.get("slack_id") or "N/A"
            c_count = str(user.get("cookies") if user.get("cookies") is not None else 0)
            
            table.add_row(str(user.get("id")), d_name, s_id, c_count)
        
        console.print(table)
        
        footer_info = f"[bold]Page {current_page}[/bold]"
        if total_pages != "Unknown":
            footer_info += f" of {total_pages}"
            
        if total_users != "Unknown":
            footer_info += f" • Total Results: {total_users}"
        
        console.print(footer_info, justify="center")
        
        if isinstance(total_pages, int) and current_page < total_pages:
             console.print(f"[dim]Tip: Use 'flavor search users \"{query}\" --page {page + 1}' to see the next page.[/dim]", justify="center")

    except APIError as e:
        console.print(f"Error: {e}", style="bold red")
