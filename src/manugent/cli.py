"""ManuGent CLI.

Command-line interface for ManuGent operations.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="manugent",
    help="🧠 ManuGent - Manufacturing Intelligence Agent",
    no_args_is_help=True,
)
console = Console()


@app.command()
def serve(
    config: Path = typer.Option(
        "configs/.env",
        "--config", "-c",
        help="Path to configuration file",
    ),
    host: str = typer.Option("0.0.0.0", "--host", help="API host"),
    port: int = typer.Option(8000, "--port", "-p", help="API port"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
    log_level: str = typer.Option("INFO", "--log-level", help="Log level"),
):
    """Start the ManuGent API server."""
    import uvicorn

    # Load config
    if config.exists():
        from dotenv import load_dotenv
        load_dotenv(config)

    rprint(Panel.fit(
        "[bold green]ManuGent[/bold green] - Manufacturing Intelligence Agent\n"
        f"API: http://{host}:{port}\n"
        f"Docs: http://{host}:{port}/docs\n"
        f"Config: {config}",
        title="🧠 Starting Server",
    ))

    uvicorn.run(
        "manugent.api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level.lower(),
    )


@app.command()
def chat(
    config: Path = typer.Option(
        "configs/.env",
        "--config", "-c",
        help="Path to configuration file",
    ),
    message: str | None = typer.Argument(None, help="Message to send"),
):
    """Interactive chat with MES Agent."""
    asyncio.run(_chat_interactive(config, message))


async def _chat_interactive(config: Path, initial_message: str | None):
    """Run interactive chat session."""
    from manugent.agent.core import MESAgent
    from manugent.config.settings import Settings
    from manugent.connector.base import MESConnectionConfig
    from manugent.connector.factory import create_connector

    settings = Settings(config)

    console.print(Panel.fit(
        "[bold]ManuGent Chat[/bold]\n"
        f"LLM: {settings.llm.provider}/{settings.llm.model}\n"
        f"MES: {settings.mes.mes_type} @ {settings.mes.mes_url}\n"
        "Type 'quit' to exit, 'clear' to clear history.",
        title="🧠 MES Agent",
    ))

    # Initialize
    llm = settings.llm.get_llm()
    mes_config = MESConnectionConfig(
        mes_type=settings.mes.mes_type,
        base_url=settings.mes.mes_url,
        auth_type="bearer" if settings.mes.mes_token else "none",
        auth_token=settings.mes.mes_token,
        auth_username=settings.mes.mes_username,
        auth_password=settings.mes.mes_password,
        timeout=settings.mes.mes_timeout,
        extra={"endpoint_mapping_path": settings.mes.mes_mapping_path},
    )
    connector = create_connector(mes_config)

    try:
        await connector.connect()
    except Exception as e:
        console.print(f"[yellow]Warning: Could not connect to MES: {e}[/yellow]")

    agent = MESAgent(llm=llm, connector=connector)

    # Process initial message or enter interactive mode
    if initial_message:
        with console.status("Thinking..."):
            response = await agent.chat(initial_message)
        console.print(Panel(response.content, title="🤖 ManuGent"))
        return

    # Interactive loop
    console.print("\n[green]Ready! Ask me anything about your factory.[/green]\n")

    while True:
        try:
            user_input = console.input("[bold blue]You> [/bold blue]").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if user_input.lower() == "clear":
            agent.clear_history()
            console.print("[dim]History cleared.[/dim]")
            continue

        with console.status("[dim]Thinking...[/dim]"):
            response = await agent.chat(user_input)

        console.print(Panel(response.content, title="🤖 ManuGent"))

        # Show tool calls if any
        if response.tool_calls:
            table = Table(title="Tools Used", show_lines=False)
            table.add_column("Tool", style="cyan")
            table.add_column("Params", style="dim")
            for tc in response.tool_calls:
                table.add_row(tc["tool"], str(tc["args"])[:60])
            console.print(table)

    console.print("\n[green]Goodbye! 👋[/green]")


@app.command()
def tools():
    """List available manufacturing tools."""
    from manugent.protocol.tools import list_tools

    table = Table(title="ManuGent Manufacturing Tools")
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Category", style="green")
    table.add_column("Safety", style="yellow")
    table.add_column("Description")

    for tool in list_tools():
        safety_color = {
            "read_only": "green",
            "advisory": "yellow",
            "approval": "red",
            "restricted": "red bold",
        }.get(tool.safety_level.value, "white")

        table.add_row(
            tool.name,
            tool.category.value,
            f"[{safety_color}]{tool.safety_level.value}[/{safety_color}]",
            tool.description[:60] + "..." if len(tool.description) > 60 else tool.description,
        )

    console.print(table)


@app.command()
def init(
    output_dir: Path = typer.Argument(".", help="Project directory"),
):
    """Initialize a new ManuGent project."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    configs_dir = output_dir / "configs"
    configs_dir.mkdir(exist_ok=True)

    env_example = configs_dir / ".env.example"
    if not env_example.exists():
        default_config = """# ManuGent Configuration
LLM_PROVIDER=ollama
LLM_API_KEY=
LLM_MODEL=gpt-4o
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

MES_TYPE=demo
MES_BASE_URL=demo://smt-factory
MES_API_TOKEN=
MES_MAPPING_PATH=

LOG_LEVEL=INFO
API_PORT=8000
"""
        env_example.write_text(default_config)
        console.print(f"[green]Created {env_example}[/green]")
    else:
        console.print(f"[dim]{env_example} already exists[/dim]")

    console.print(Panel.fit(
        "ManuGent project initialized!\n\n"
        "Next steps:\n"
        "1. Copy configs/.env.example to configs/.env\n"
        "2. Fill in your LLM and MES settings\n"
        "3. Run: manugent serve",
        title="✅ Init Complete",
    ))


@app.command()
def version():
    """Show version."""
    from manugent import __version__
    console.print(f"ManuGent v{__version__}")


def main():
    """Entry point."""
    app()


if __name__ == "__main__":
    main()
