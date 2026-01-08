# flavor/cli.py
import typer
import time
from rich.console import Console
from rich.table import Table
from flavor.config import set_api_key, set_flavor_id, get_flavor_id, set_hackatime_key, set_hackatime_username, get_hackatime_username
from flavor.api import get_users, get_user_by_id, APIError, get_shop, get_project
from flavor.hackatime import get_time_today, get_stats, HackatimeAPIError

app = typer.Typer()
cookies_app = typer.Typer()
list_app = typer.Typer()
time_app = typer.Typer()
login_app = typer.Typer()
search_app = typer.Typer()

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
    
@app.command()
def status():
    """Check FLT's status (if for some reason you feel you have to)."""
    console.print("FlavorLineTool is alive, I think!!!", style="blink green")

@login_app.command("api")
def login_api(key: str):
    """Login with your Flavortown API key."""
    if not key.startswith("ft_sk_"):
        console.print("Invalid API key format. It must start with 'ft_sk_'.", style="bold red")
        raise typer.Exit(code=1)
    
    set_api_key(key)
    console.print(f"Successfully logged in with to Flavortown API!", style="green")

@login_app.command("id")
def login_id(key: str):
    """Login with your Flavortown UserID."""
    set_flavor_id(key)
    console.print(f"Successfully logged in with the Flavortown User ID!", style="green")

@login_app.command("hackatime")
def login_hackatime(key: str):
    """Login with your Hackatime API key."""
    set_hackatime_key(key)
    console.print(f"Successfully logged in with Hackatime API key!", style="green")

@login_app.command("hackatimeuser")
def login_hackatime_user(username: str):
    """Set your Hackatime username."""
    set_hackatime_username(username)
    console.print(f"Successfully set Hackatime username to {username}!", style="green")

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
def list_users(page: int = 1):
    """List users (paginated)."""
    try:
        with console.status(f"Fetching users (page {page})...", spinner="dots"):
            data = get_users(page)
        
        users = data.get("users", [])
        
        if not users:
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

        for user in users:
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

@list_app.command("my-projects")
def list_my_projects():
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

@time_app.command("today")
def time_today():
    """Show how much you've coded today."""
    try:
        with console.status("Fetching your coding time...", spinner="dots"):
            data = get_time_today()
        
        grand_total = data.get("data", {}).get("grand_total", {})
        text = grand_total.get("text", "0 secs")
        
        console.print(f"You have coded for [bold cyan]{text}[/bold cyan] today!", style="green")
        
    except HackatimeAPIError as e:
        console.print(f"Error: {e}", style="bold red")

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
                # Stop spinner to prompt user
                pass 
        
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
        console.print(f"Flavortown Error: {e}", style="bold red")
    except HackatimeAPIError as e:
        console.print(f"Hackatime Error: {e}", style="bold red")
    except ValueError:
        console.print("Stored Flavor ID is not a valid integer.", style="bold red")

@search_app.command("users")
def search_users(query: str):
    """
    Search for users by display name (client-side). WARNING: EXPERIMENTAL FEATURE / PROOF OF CONCEPT due to high API usage.
    """
    console.print("[bold red]WARNING: This is an EXPERIMENTAL FEATURE and mostly a PROOF OF CONCEPT.[/bold red]")
    console.print("[bold red]It performs client-side filtering by iterating through paginated API results.[/bold red]")
    console.print("[bold red]HIGH RISK of hitting API rate limits. Advised against using for now.[/bold red]", style="bold red")
    console.print()

    if not typer.confirm("Do you want to proceed despite the risks?"):
        console.print("Aborted.", style="yellow")
        raise typer.Exit()

    query_norm = query.lower().strip()
    console.print(f"Searching for users matching '[bold]{query}[/bold]'...", style="cyan")

    try:
        with console.status(f"Fetching page 1...", spinner="dots"):
             data = get_users(page=1)
             
        users = data.get("users", [])
        pagination = data.get("pagination", {})
        total_pages = pagination.get("total_pages", 1)
        total_count = pagination.get("total_count", "Unknown")
        
        results = []
        def filter_users(user_list):
            matches = []
            for u in user_list:
                d_name = u.get("display_name") or ""
                if query_norm in d_name.lower():
                    matches.append(u)
            return matches

        results.extend(filter_users(users))
        
        console.print(f"Found {len(results)} matches on Page 1.", style="dim")
        
        if total_pages > 1:
            console.print(f"There are {total_pages} pages ({total_count} users) total.", style="yellow")
            console.print("Warning: API Rate Limit is 5 reqs/min.", style="bold red")
            
            if typer.confirm("Do you want to scan ALL pages? (This will take several minutes)"):
                import time
                from rich.progress import track
                
                pages_to_scan = range(2, total_pages + 1)
                
                for page_num in track(pages_to_scan, description="Scanning pages..."):
                    # Rate limit sleep - 12s per request to be safe (5 reqs/60s)
                    time.sleep(12.5) 
                    
                    try:
                        p_data = get_users(page=page_num)
                        page_users = p_data.get("users", [])
                        matches = filter_users(page_users)
                        if matches:
                            results.extend(matches)
                            console.print(f"Found {len(matches)} matches on Page {page_num}...", style="dim")
                    except Exception as e:
                        console.print(f"Failed to fetch page {page_num}: {e}", style="red")
                        # Don't break, try next?
                        pass

        # Display results
        if not results:
            console.print("No users found.", style="yellow")
            return

        title = f"Search Results for '{query}'"
        table = Table(title=title)
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="magenta")
        table.add_column("Slack ID", style="green")
        table.add_column("Cookies", justify="right", style="yellow")

        for user in results:
            d_name = user.get("display_name") or "Unknown"
            s_id = user.get("slack_id") or "N/A"
            c_count = str(user.get("cookies") if user.get("cookies") is not None else 0)
            table.add_row(str(user.get("id")), d_name, s_id, c_count)

        console.print(table)
        console.print(f"Total found: {len(results)}", justify="center", style="bold")

    except APIError as e:
        console.print(f"Error: {e}", style="bold red")

def main():
    app()

if __name__ == "__main__":
    main()
