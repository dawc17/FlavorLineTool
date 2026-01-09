import typer
from rich.console import Console
from rich.table import Table
from flavor.config import get_flavor_id, set_flavor_id
from flavor.api import get_shop, get_users, get_user_by_id, get_project, APIError

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command("shop")
def shop():
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

@app.command("users")
def users(page: int = 1):
    """List users (paginated)."""
    try:
        with console.status(f"Fetching users (page {page})...", spinner="dots"):
            data = get_users(page)
        
        users_list = data.get("users", [])
        
        if not users_list:
            console.print("No users found on this page.", style="yellow")
            return

        pagination = data.get("pagination", {})
        total_users = pagination.get("total_count", "Unknown")
        current_page = pagination.get("current_page", page)
        total_pages = pagination.get("total_pages", "Unknown")
        
        title = "Flavortown Users"
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
            footer_info += f" • Total Users: {total_users}"
        
        console.print(footer_info, justify="center")
        console.print(f"[dim]Tip: Use 'flavor list users --page {page + 1}' to see the next page.[/dim]", justify="center")

    except APIError as e:
        console.print(f"Error: {e}", style="bold red")

@app.command("my-projects")
def my_projects():
    """List your projects on Flavortown."""
    flavor_id = get_flavor_id()
    if not flavor_id:
        console.print("You are not logged in with your Flavor ID.", style="yellow")
        flavor_id = typer.prompt("Please enter your Flavortown User ID")
        set_flavor_id(flavor_id)
        console.print(f"Flavor ID saved!", style="green")
        
    try:
        with console.status("Fetching your profile...", spinner="dots"):
            user_data = get_user_by_id(int(flavor_id))
        
        project_ids = user_data.get("project_ids", [])
        if not project_ids:
            console.print("You have no projects linked to your profile.", style="yellow")
            return
            
        console.print(f"Found {len(project_ids)} projects. Fetching details...", style="cyan")
        
        projects = []
        with console.status("Fetching project details...", spinner="dots"):
            for pid in project_ids:
                try:
                    p_data = get_project(pid)
                    projects.append(p_data)
                except APIError as e:
                    console.print(f"Failed to fetch project {pid}: {e}", style="red")

        if not projects:
            console.print("No project details could be retrieved.", style="red")
            return

        table = Table(title="Your Projects")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("Description", style="white")
        table.add_column("Repo URL", style="blue")
        
        for project in projects:
            p_id = str(project.get("id"))
            title = project.get("title") or "Unknown"
            desc = project.get("description") or "-"
            if len(desc) > 50:
                desc = desc[:47] + "..."
            repo = project.get("repo_url") or "-"
            
            table.add_row(p_id, title, desc, repo)
            
        console.print(table)

    except APIError as e:
        console.print(f"Error: {e}", style="bold red")
    except ValueError:
        console.print("Stored Flavor ID is not a valid integer.", style="bold red")
