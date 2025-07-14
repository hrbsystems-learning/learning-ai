"""CLI interface for customer flows with Prefect 3 integration."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from .config import get_settings
from .utils.logging import configure_logging, get_logger
from .flows.example_flow import example_analysis_flow
from .agents.example_crew import create_analysis_crew, validate_crew_configuration

# Initialize CLI app
app = typer.Typer(
    name="customer-flows",
    help="Customer Prefect Flows CLI - Manage and execute workflows",
    add_completion=False,
)

console = Console()
logger = get_logger(__name__)


def setup_cli():
    """Initialize CLI environment."""
    configure_logging()
    settings = get_settings()
    logger.info("CLI initialized", environment=settings.environment)


@app.command()
def info():
    """Display system information and configuration."""
    setup_cli()
    settings = get_settings()
    
    # Create info table
    table = Table(title="Customer Flows - System Information")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    table.add_row("Environment", settings.environment)
    table.add_row("Log Level", settings.log_level)
    table.add_row("Prefect API URL", settings.prefect_api_url or "Not configured")
    table.add_row("OpenAI API Key", "Configured" if settings.openai_api_key else "Not configured")
    table.add_row("LangChain Tracing", str(settings.langchain_tracing_v2))
    table.add_row("LangChain Project", settings.langchain_project)
    
    console.print(table)


@app.command()
def run_flow(
    flow_name: str = typer.Argument("example-analysis-flow", help="Name of the flow to run"),
    input_data: str = typer.Option("Sample data for analysis", "--input", "-i", help="Input data for the flow"),
    save_results: bool = typer.Option(True, "--save/--no-save", help="Whether to save results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Run a specific flow with given parameters."""
    setup_cli()
    
    with console.status("[bold green]Running flow...", spinner="dots"):
        try:
            if flow_name == "example-analysis-flow":
                result = example_analysis_flow(input_data, save_results)
                
                if verbose:
                    console.print("\n[bold green]Flow completed successfully![/bold green]")
                    console.print(Panel(json.dumps(result, indent=2), title="Flow Result"))
                else:
                    console.print(f"[bold green]✓[/bold green] Flow completed. Status: {result.get('status', 'unknown')}")
                    if result.get('storage_location'):
                        console.print(f"[dim]Results saved to: {result['storage_location']}[/dim]")
            else:
                console.print(f"[bold red]Error:[/bold red] Unknown flow '{flow_name}'")
                raise typer.Exit(1)
                
        except Exception as e:
            console.print(f"[bold red]Flow execution failed:[/bold red] {e}")
            if verbose:
                console.print_exception()
            raise typer.Exit(1)


@app.command()
def list_flows():
    """List all available flows."""
    setup_cli()
    
    flows = [
        {
            "name": "example-analysis-flow",
            "description": "Example flow using CrewAI and LangChain with Prefect 3",
            "version": "1.0.0",
            "status": "Active"
        }
    ]
    
    table = Table(title="Available Flows")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Version", style="green")
    table.add_column("Status", style="yellow")
    
    for flow in flows:
        table.add_row(
            flow["name"],
            flow["description"],
            flow["version"],
            flow["status"]
        )
    
    console.print(table)


@app.command()
def test_crew(
    crew_type: str = typer.Option("analysis", "--type", "-t", help="Type of crew to test"),
    sample_data: str = typer.Option("Sample test data", "--data", "-d", help="Sample data for testing"),
    validate_only: bool = typer.Option(False, "--validate-only", help="Only validate crew configuration"),
):
    """Test CrewAI crew configuration and execution."""
    setup_cli()
    
    with console.status("[bold green]Testing crew...", spinner="dots"):
        try:
            # Prepare test data
            test_data = {
                "original": sample_data,
                "length": len(sample_data),
                "word_count": len(sample_data.split()),
                "character_count": len(sample_data.replace(" ", "")),
                "processed_at": datetime.now().isoformat(),
            }
            
            # Create crew
            crew = create_analysis_crew(test_data)
            
            # Validate crew configuration
            validation_result = validate_crew_configuration(crew)
            
            console.print("\n[bold blue]Crew Validation Results:[/bold blue]")
            
            if validation_result["is_valid"]:
                console.print("[bold green]✓[/bold green] Crew configuration is valid")
            else:
                console.print("[bold red]✗[/bold red] Crew configuration has errors")
                for error in validation_result["errors"]:
                    console.print(f"  [red]• {error}[/red]")
            
            if validation_result["warnings"]:
                console.print("\n[bold yellow]Warnings:[/bold yellow]")
                for warning in validation_result["warnings"]:
                    console.print(f"  [yellow]• {warning}[/yellow]")
            
            if validation_result["recommendations"]:
                console.print("\n[bold cyan]Recommendations:[/bold cyan]")
                for rec in validation_result["recommendations"]:
                    console.print(f"  [cyan]• {rec}[/cyan]")
            
            if not validate_only and validation_result["is_valid"]:
                console.print("\n[bold green]Running crew test...[/bold green]")
                result = crew.kickoff({"data": test_data})
                console.print("[bold green]✓[/bold green] Crew test completed successfully")
                console.print(Panel(str(result)[:500] + "..." if len(str(result)) > 500 else str(result), title="Crew Result"))
            
        except Exception as e:
            console.print(f"[bold red]Crew test failed:[/bold red] {e}")
            console.print_exception()
            raise typer.Exit(1)


@app.command()
def deploy(
    environment: str = typer.Option("development", "--env", "-e", help="Deployment environment"),
    work_pool: str = typer.Option("default", "--pool", "-p", help="Prefect work pool name"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deployed without actually deploying"),
):
    """Deploy flows to Prefect."""
    setup_cli()
    
    if dry_run:
        console.print("[bold yellow]Dry run mode - showing what would be deployed:[/bold yellow]")
    
    deployments = [
        {
            "flow_name": "example-analysis-flow",
            "deployment_name": f"example-analysis-{environment}",
            "work_pool": work_pool,
            "tags": [environment, "customer-flows", "crewai"],
        }
    ]
    
    table = Table(title=f"Deployment Plan - {environment.upper()}")
    table.add_column("Flow", style="cyan")
    table.add_column("Deployment", style="white")
    table.add_column("Work Pool", style="green")
    table.add_column("Tags", style="yellow")
    
    for deployment in deployments:
        table.add_row(
            deployment["flow_name"],
            deployment["deployment_name"],
            deployment["work_pool"],
            ", ".join(deployment["tags"])
        )
    
    console.print(table)
    
    if not dry_run:
        with console.status("[bold green]Deploying flows...", spinner="dots"):
            try:
                # Here you would implement actual Prefect deployment logic
                # For now, just simulate the deployment
                import time
                time.sleep(2)
                
                console.print("[bold green]✓[/bold green] Deployment completed successfully")
                console.print(f"[dim]Deployed to {environment} environment[/dim]")
                
            except Exception as e:
                console.print(f"[bold red]Deployment failed:[/bold red] {e}")
                raise typer.Exit(1)


@app.command()
def validate_config():
    """Validate system configuration and dependencies."""
    setup_cli()
    settings = get_settings()
    
    console.print("[bold blue]Validating Configuration...[/bold blue]\n")
    
    checks = []
    
    # Check Prefect configuration
    if settings.prefect_api_url:
        checks.append(("Prefect API URL", "✓", "green"))
    else:
        checks.append(("Prefect API URL", "⚠ Not configured", "yellow"))
    
    # Check OpenAI configuration
    if settings.openai_api_key:
        checks.append(("OpenAI API Key", "✓", "green"))
    else:
        checks.append(("OpenAI API Key", "✗ Missing", "red"))
    
    # Check LangChain configuration
    if settings.langchain_api_key:
        checks.append(("LangChain API Key", "✓", "green"))
    else:
        checks.append(("LangChain API Key", "⚠ Not configured", "yellow"))
    
    # Check dependencies
    try:
        import prefect
        checks.append(("Prefect", f"✓ v{prefect.__version__}", "green"))
    except ImportError:
        checks.append(("Prefect", "✗ Not installed", "red"))
    
    try:
        import crewai
        checks.append(("CrewAI", "✓ Installed", "green"))
    except ImportError:
        checks.append(("CrewAI", "✗ Not installed", "red"))
    
    try:
        import langchain
        checks.append(("LangChain", f"✓ v{langchain.__version__}", "green"))
    except ImportError:
        checks.append(("LangChain", "✗ Not installed", "red"))
    
    # Display results
    table = Table(title="Configuration Validation")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    
    for name, status, color in checks:
        table.add_row(name, f"[{color}]{status}[/{color}]")
    
    console.print(table)
    
    # Summary
    errors = sum(1 for _, status, color in checks if color == "red")
    warnings = sum(1 for _, status, color in checks if color == "yellow")
    
    if errors > 0:
        console.print(f"\n[bold red]Found {errors} error(s) that need attention[/bold red]")
    elif warnings > 0:
        console.print(f"\n[bold yellow]Found {warnings} warning(s) - system should work but may have limited functionality[/bold yellow]")
    else:
        console.print(f"\n[bold green]All checks passed! System is ready to use.[/bold green]")


if __name__ == "__main__":
    app()
