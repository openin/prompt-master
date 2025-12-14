import json
import os
from typing import Annotated

import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel

from .analyzer import PromptAnalyzer

app = typer.Typer(help="Prompt Master - AI Prompt Linter")
console = Console()


@app.command()
def analyze(
    prompt: Annotated[str, typer.Argument(help="The prompt text or file path")],
    model: str = "gemini-2.0-flash",
    json_output: bool = False,
):
    """
    Audit a specific prompt via CLI.
    """
    # Load from file if argument is a path
    if os.path.exists(prompt):
        with open(prompt, encoding="utf-8") as f:
            prompt_text = f.read()
    else:
        prompt_text = prompt

    try:
        analyzer = PromptAnalyzer(model_name=model)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1) from None

    with console.status("[bold green]Asking Gemini to audit your prompt...[/bold green]"):
        result = analyzer.analyze_sync(prompt_text)

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        _print_rich_report(result)


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """
    Start the FastAPI server.
    """
    console.print(f"[bold green]🚀 Starting Prompt Master API on http://{host}:{port}[/bold green]")
    uvicorn.run("prompt_master.api:app", host=host, port=port, reload=reload)


def _print_rich_report(data):
    score = data.get("score", 0)
    color = "green" if score >= 8 else "yellow" if score >= 5 else "red"

    console.print()
    console.print(
        Panel(f"[bold {color}]Score: {score}/10[/bold {color}]", title="Audit Result", expand=False)
    )

    console.print(f"[bold]Summary:[/bold] {data.get('summary')}")
    console.print()

    if data.get("suggestions"):
        console.print("[bold yellow]⚠️  Improvements Needed:[/bold yellow]")
        for item in data["suggestions"]:
            console.print(f" • [bold]Rule {item['rule']}:[/bold] {item['advice']}")

    console.print()
    console.print("[dim]Based on Google's 10 Golden Rules of Prompting[/dim]")


if __name__ == "__main__":
    app()
