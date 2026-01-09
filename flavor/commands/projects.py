import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from flavor.api import get_project, get_user_by_id, create_project, update_project, APIError
from flavor.config import get_flavor_id, get_api_key, set_flavor_id

app = typer.Typer(no_args_is_help=True)
console = Console()

def _check_authenticated() -> dict:
    """
    Check if the user is authenticated with both API key and Flavor ID.
    Returns the user data if authenticated.
    """
    api_key = get_api_key()
    if not api_key:
        console.print("[bold red]❌ You must be logged in with your Flavortown API key.[/bold red]")
        console.print("[dim]Run 'flavor login api' to authenticate.[/dim]")
        raise typer.Exit(code=1)
    
    flavor_id = get_flavor_id()
    if not flavor_id:
        console.print("[bold yellow]⚠️  You haven't set your Flavortown User ID yet.[/bold yellow]")
        flavor_id = Prompt.ask("Please enter your Flavortown User ID")
        set_flavor_id(flavor_id)
        console.print("[green]Flavor ID saved![/green]")
    
    try:
        user_data = get_user_by_id(int(flavor_id))
        return user_data
    except APIError as e:
        console.print(f"[bold red]❌ Failed to verify your identity: {e}[/bold red]")
        raise typer.Exit(code=1)
    except ValueError:
        console.print("[bold red]❌ Invalid Flavor ID format.[/bold red]")
        raise typer.Exit(code=1)

def _check_project_ownership(user_data: dict, project_id: int) -> bool:
    """Check if the user owns the project."""
    project_ids = user_data.get("project_ids", [])
    return project_id in project_ids

def _display_project_summary(project: dict, title: str = "Project Summary"):
    """Display a formatted project summary."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("ID", str(project.get("id", "N/A")))
    table.add_row("Title", project.get("title") or "-")
    table.add_row("Description", project.get("description") or "-")
    table.add_row("Repo URL", project.get("repo_url") or "-")
    table.add_row("Demo URL", project.get("demo_url") or "-")
    table.add_row("README URL", project.get("readme_url") or "-")
    table.add_row("Created", project.get("created_at") or "-")
    table.add_row("Updated", project.get("updated_at") or "-")
    
    console.print(Panel(table, title=f"[bold magenta]{title}[/bold magenta]", border_style="magenta"))

def _project_form(existing: dict = None) -> dict:
    """
    Interactive form for project creation/editing.
    Returns a dict with the form values.
    """
    is_edit = existing is not None
    mode = "Edit" if is_edit else "New"
    
    # Header
    console.print()
    header = Text(f"📦 {mode} Project Form", style="bold cyan")
    console.print(Panel(Align.center(header), border_style="cyan"))
    console.print()
    
    if is_edit:
        console.print("[dim]Press Enter to keep existing values, or type a new value.[/dim]")
        console.print("[dim]Type '-' to clear an optional field.[/dim]")
        console.print()
    
    # Form fields
    fields = {}
    
    # Title (required for new, optional for edit)
    default_title = existing.get("title", "") if existing else ""
    console.print("[bold]1/5[/bold] [cyan]Title[/cyan] [red](required)[/red]")
    if is_edit:
        console.print(f"   [dim]Current: {default_title}[/dim]")
    title_input = Prompt.ask("   Enter title", default=default_title if is_edit else "")
    if not is_edit and not title_input.strip():
        console.print("[red]Title is required![/red]")
        raise typer.Exit(code=1)
    fields["title"] = title_input.strip() if title_input.strip() else (default_title if is_edit else None)
    console.print()
    
    # Description (required for new, optional for edit)
    default_desc = existing.get("description", "") if existing else ""
    console.print("[bold]2/5[/bold] [cyan]Description[/cyan] [red](required)[/red]")
    if is_edit:
        display_desc = default_desc[:50] + "..." if len(default_desc) > 50 else default_desc
        console.print(f"   [dim]Current: {display_desc}[/dim]")
    desc_input = Prompt.ask("   Enter description", default=default_desc if is_edit else "")
    if not is_edit and not desc_input.strip():
        console.print("[red]Description is required![/red]")
        raise typer.Exit(code=1)
    fields["description"] = desc_input.strip() if desc_input.strip() else (default_desc if is_edit else None)
    console.print()
    
    # Repo URL (optional)
    default_repo = existing.get("repo_url", "") if existing else ""
    console.print("[bold]3/5[/bold] [cyan]Repository URL[/cyan] [dim](optional)[/dim]")
    if is_edit and default_repo:
        console.print(f"   [dim]Current: {default_repo}[/dim]")
    repo_input = Prompt.ask("   Enter repo URL", default=default_repo if is_edit else "")
    if repo_input.strip() == "-":
        fields["repo_url"] = ""
    elif repo_input.strip():
        fields["repo_url"] = repo_input.strip()
    elif is_edit:
        fields["repo_url"] = None  # Don't update
    else:
        fields["repo_url"] = None
    console.print()
    
    # Demo URL (optional)
    default_demo = existing.get("demo_url", "") if existing else ""
    console.print("[bold]4/5[/bold] [cyan]Demo URL[/cyan] [dim](optional)[/dim]")
    if is_edit and default_demo:
        console.print(f"   [dim]Current: {default_demo}[/dim]")
    demo_input = Prompt.ask("   Enter demo URL", default=default_demo if is_edit else "")
    if demo_input.strip() == "-":
        fields["demo_url"] = ""
    elif demo_input.strip():
        fields["demo_url"] = demo_input.strip()
    elif is_edit:
        fields["demo_url"] = None  # Don't update
    else:
        fields["demo_url"] = None
    console.print()
    
    # README URL (optional)
    default_readme = existing.get("readme_url", "") if existing else ""
    console.print("[bold]5/5[/bold] [cyan]README URL[/cyan] [dim](optional)[/dim]")
    if is_edit and default_readme:
        console.print(f"   [dim]Current: {default_readme}[/dim]")
    readme_input = Prompt.ask("   Enter README URL", default=default_readme if is_edit else "")
    if readme_input.strip() == "-":
        fields["readme_url"] = ""
    elif readme_input.strip():
        fields["readme_url"] = readme_input.strip()
    elif is_edit:
        fields["readme_url"] = None  # Don't update
    else:
        fields["readme_url"] = None
    console.print()
    
    return fields

@app.command("create")
def project_create():
    """Create a new project with an interactive form."""
    console.print()
    console.print("[bold cyan]🚀 Create New Project[/bold cyan]")
    console.print("[dim]Fill out the form below to create a new project.[/dim]")
    console.print()
    
    # Check authentication
    with console.status("Verifying your identity...", spinner="dots"):
        user_data = _check_authenticated()
    
    display_name = user_data.get("display_name", "Unknown")
    console.print(f"[green]✓ Authenticated as [bold]{display_name}[/bold][/green]")
    console.print()
    
    try:
        fields = _project_form()
        
        # Preview
        console.print("[bold]Preview[/bold]")
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        preview_data = {
            "title": fields["title"],
            "description": fields["description"],
            "repo_url": fields["repo_url"] or "-",
            "demo_url": fields["demo_url"] or "-",
            "readme_url": fields["readme_url"] or "-",
        }
        
        for key, val in preview_data.items():
            table.add_row(key.replace("_", " ").title(), str(val))
        console.print(table)
        console.print()
        
        # Confirm
        if not Confirm.ask("[yellow]Create this project?[/yellow]", default=True):
            console.print("[dim]Cancelled.[/dim]")
            raise typer.Exit()
        
        # Submit
        with console.status("Creating project...", spinner="dots"):
            result = create_project(
                title=fields["title"],
                description=fields["description"],
                repo_url=fields["repo_url"],
                demo_url=fields["demo_url"],
                readme_url=fields["readme_url"],
            )
        
        console.print()
        console.print("[bold green]✅ Project created successfully![/bold green]")
        _display_project_summary(result, "Created Project")
        
    except APIError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("edit")
def project_edit(project_id: int = typer.Argument(None, help="The ID of the project to edit")):
    """Edit an existing project with an interactive form."""
    if project_id is None:
        project_id = int(Prompt.ask("Enter the project ID to edit"))
    
    console.print()
    console.print(f"[bold cyan]✏️  Edit Project #{project_id}[/bold cyan]")
    console.print()
    
    # Check authentication
    with console.status("Verifying your identity...", spinner="dots"):
        user_data = _check_authenticated()
    
    display_name = user_data.get("display_name", "Unknown")
    console.print(f"[green]✓ Authenticated as [bold]{display_name}[/bold][/green]")
    
    # Check ownership
    if not _check_project_ownership(user_data, project_id):
        console.print()
        console.print(f"[bold red]❌ You don't own project #{project_id}.[/bold red]")
        console.print("[dim]You can only edit projects that belong to you.[/dim]")
        
        # Show user's projects
        user_projects = user_data.get("project_ids", [])
        if user_projects:
            console.print(f"\n[cyan]Your project IDs:[/cyan] {', '.join(map(str, user_projects))}")
        else:
            console.print("\n[yellow]You don't have any projects yet. Create one with 'flavor projects create'.[/yellow]")
        
        raise typer.Exit(code=1)
    
    console.print(f"[green]✓ Ownership verified[/green]")
    console.print()
    
    try:
        # Fetch existing project
        with console.status("Fetching project...", spinner="dots"):
            existing = get_project(project_id)
        
        _display_project_summary(existing, "Current Project Data")
        console.print()
        
        if not Confirm.ask("[yellow]Continue editing this project?[/yellow]", default=True):
            console.print("[dim]Cancelled.[/dim]")
            raise typer.Exit()
        
        fields = _project_form(existing=existing)
        
        # Filter out None values (unchanged fields)
        updates = {k: v for k, v in fields.items() if v is not None}
        
        if not updates:
            console.print("[yellow]No changes made.[/yellow]")
            raise typer.Exit()
        
        # Preview changes
        console.print("[bold]Changes to Apply[/bold]")
        table = Table(show_header=True, box=None, padding=(0, 2))
        table.add_column("Field", style="cyan")
        table.add_column("Old Value", style="red")
        table.add_column("New Value", style="green")
        
        for key, new_val in updates.items():
            old_val = existing.get(key) or "-"
            display_new = new_val if new_val else "[cleared]"
            if old_val != new_val:
                table.add_row(key.replace("_", " ").title(), str(old_val), str(display_new))
        
        console.print(table)
        console.print()
        
        # Confirm
        if not Confirm.ask("[yellow]Apply these changes?[/yellow]", default=True):
            console.print("[dim]Cancelled.[/dim]")
            raise typer.Exit()
        
        # Submit
        with console.status("Updating project...", spinner="dots"):
            result = update_project(
                project_id=project_id,
                title=updates.get("title"),
                description=updates.get("description"),
                repo_url=updates.get("repo_url"),
                demo_url=updates.get("demo_url"),
                readme_url=updates.get("readme_url"),
            )
        
        console.print()
        console.print("[bold green]✅ Project updated successfully![/bold green]")
        _display_project_summary(result, "Updated Project")
        
    except APIError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("view")
def project_view(project_id: int = typer.Argument(None, help="The ID of the project to view")):
    """View details of a specific project."""
    if project_id is None:
        project_id = int(Prompt.ask("Enter the project ID to view"))
    
    try:
        with console.status("Fetching project...", spinner="dots"):
            project = get_project(project_id)
        
        console.print()
        _display_project_summary(project, f"Project #{project_id}")
        
        # Show devlog IDs if any
        devlog_ids = project.get("devlog_ids", [])
        if devlog_ids:
            console.print(f"\n[cyan]Devlogs:[/cyan] {', '.join(map(str, devlog_ids))}")
        
    except APIError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)
