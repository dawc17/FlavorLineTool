# flavor/cli.py
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.callback()
def callback():
    """
    FlavorLineTool - A CLI for tracking cookies and interacting with Flavortown.
    """
    
@app.command()
def status():
    console.print("FlavorLineTool is alive!!!", style="bold green")

def main():
    app()

if __name__ == "__main__":
    main()
