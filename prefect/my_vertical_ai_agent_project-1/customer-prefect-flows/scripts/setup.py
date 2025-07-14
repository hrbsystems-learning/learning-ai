#!/usr/bin/env python3
"""Setup script for local development environment."""

import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer()


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    typer.echo(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result


@app.command()
def install():
    """Install project dependencies."""
    typer.echo("Installing project dependencies...")
    
    # Install production dependencies
    run_command("pip install -r requirements.txt")
    
    # Install development dependencies
    run_command("pip install -r requirements-dev.txt")
    
    # Install project in development mode
    run_command("pip install -e .")
    
    typer.echo("✅ Dependencies installed successfully!")


@app.command()
def setup_env():
    """Setup environment configuration."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        typer.echo("⚠️  .env file already exists")
        overwrite = typer.confirm("Do you want to overwrite it?")
        if not overwrite:
            return
    
    if env_example.exists():
        # Copy example to .env
        content = env_example.read_text()
        env_file.write_text(content)
        typer.echo("✅ Created .env file from .env.example")
        typer.echo("📝 Please edit .env file with your configuration")
    else:
        typer.echo("❌ .env.example file not found")


@app.command()
def setup_precommit():
    """Setup pre-commit hooks."""
    typer.echo("Setting up pre-commit hooks...")
    
    # Install pre-commit hooks
    run_command("pre-commit install")
    
    # Run pre-commit on all files
    run_command("pre-commit run --all-files", check=False)
    
    typer.echo("✅ Pre-commit hooks setup complete!")


@app.command()
def check():
    """Run code quality checks."""
    typer.echo("Running code quality checks...")
    
    # Run linting
    typer.echo("\n🔍 Running ruff...")
    run_command("ruff check src/", check=False)
    
    # Run formatting check
    typer.echo("\n🎨 Checking code formatting...")
    run_command("black --check src/", check=False)
    
    # Run type checking
    typer.echo("\n🔍 Running type checks...")
    run_command("mypy src/", check=False)
    
    typer.echo("\n✅ Quality checks complete!")


@app.command()
def format_code():
    """Format code with black and ruff."""
    typer.echo("Formatting code...")
    
    # Run ruff fixes
    run_command("ruff check src/ --fix")
    
    # Run black formatting
    run_command("black src/")
    
    typer.echo("✅ Code formatted!")


@app.command()
def test():
    """Run tests."""
    typer.echo("Running tests...")
    
    # Run pytest
    run_command("pytest tests/ -v")
    
    typer.echo("✅ Tests complete!")


@app.command()
def test_coverage():
    """Run tests with coverage."""
    typer.echo("Running tests with coverage...")
    
    # Run pytest with coverage
    run_command("pytest tests/ --cov=src --cov-report=html --cov-report=term-missing")
    
    typer.echo("✅ Coverage report generated!")
    typer.echo("📊 Open htmlcov/index.html to view detailed coverage report")


@app.command()
def clean():
    """Clean up generated files."""
    typer.echo("Cleaning up...")
    
    # Remove Python cache
    run_command("find . -type d -name __pycache__ -exec rm -rf {} +", check=False)
    run_command("find . -name '*.pyc' -delete", check=False)
    
    # Remove test artifacts
    run_command("rm -rf htmlcov/", check=False)
    run_command("rm -rf .coverage", check=False)
    run_command("rm -rf .pytest_cache/", check=False)
    
    # Remove build artifacts
    run_command("rm -rf build/", check=False)
    run_command("rm -rf dist/", check=False)
    run_command("rm -rf *.egg-info/", check=False)
    
    typer.echo("✅ Cleanup complete!")


@app.command()
def all():
    """Run complete setup (install, env, pre-commit)."""
    typer.echo("🚀 Running complete setup...")
    
    install()
    setup_env()
    setup_precommit()
    
    typer.echo("🎉 Setup complete!")
    typer.echo("📝 Next steps:")
    typer.echo("  1. Edit .env file with your configuration")
    typer.echo("  2. Run 'python scripts/setup.py test' to verify installation")
    typer.echo("  3. Start developing your flows!")


if __name__ == "__main__":
    app()
