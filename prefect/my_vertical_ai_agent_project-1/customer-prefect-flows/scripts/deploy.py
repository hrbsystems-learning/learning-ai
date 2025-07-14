#!/usr/bin/env python3
"""Deployment script for Prefect flows."""

import asyncio
import sys
from pathlib import Path
from typing import List

import typer
from prefect import get_client
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from customer_flows.flows.example_flow import example_analysis_flow
from customer_flows.utils.logging import get_logger

logger = get_logger(__name__)
app = typer.Typer()


async def create_deployment(
    flow_function,
    name: str,
    description: str,
    schedule: str = None,
    work_pool: str = "default",
) -> str:
    """Create a Prefect deployment."""
    logger.info("Creating deployment", name=name)
    
    deployment_config = {
        "name": name,
        "description": description,
        "work_pool_name": work_pool,
        "path": str(Path.cwd()),
    }
    
    if schedule:
        deployment_config["schedule"] = CronSchedule(cron=schedule)
    
    deployment = Deployment.build_from_flow(
        flow=flow_function,
        **deployment_config
    )
    
    deployment_id = await deployment.apply()
    logger.info("Deployment created", deployment_id=deployment_id)
    return deployment_id


@app.command()
def deploy_all(
    work_pool: str = typer.Option("default", help="Work pool name"),
    schedule_example: str = typer.Option(None, help="Cron schedule for example flow"),
):
    """Deploy all flows to Prefect."""
    async def _deploy():
        logger.info("Starting deployment of all flows")
        
        deployments = [
            {
                "flow": example_analysis_flow,
                "name": "example-analysis-deployment",
                "description": "Example analysis flow with CrewAI and LangChain",
                "schedule": schedule_example,
            },
        ]
        
        deployment_ids = []
        for config in deployments:
            deployment_id = await create_deployment(
                flow_function=config["flow"],
                name=config["name"],
                description=config["description"],
                schedule=config["schedule"],
                work_pool=work_pool,
            )
            deployment_ids.append(deployment_id)
        
        logger.info("All deployments completed", count=len(deployment_ids))
        return deployment_ids
    
    return asyncio.run(_deploy())


@app.command()
def deploy_single(
    flow_name: str = typer.Argument(..., help="Name of the flow to deploy"),
    deployment_name: str = typer.Option(None, help="Custom deployment name"),
    work_pool: str = typer.Option("default", help="Work pool name"),
    schedule: str = typer.Option(None, help="Cron schedule"),
):
    """Deploy a single flow."""
    async def _deploy():
        # Map flow names to functions
        flows = {
            "example_analysis_flow": example_analysis_flow,
        }
        
        if flow_name not in flows:
            typer.echo(f"Unknown flow: {flow_name}")
            typer.echo(f"Available flows: {list(flows.keys())}")
            raise typer.Exit(1)
        
        flow_function = flows[flow_name]
        name = deployment_name or f"{flow_name}-deployment"
        
        deployment_id = await create_deployment(
            flow_function=flow_function,
            name=name,
            description=f"Deployment for {flow_name}",
            schedule=schedule,
            work_pool=work_pool,
        )
        
        typer.echo(f"Deployed {flow_name} with ID: {deployment_id}")
        return deployment_id
    
    return asyncio.run(_deploy())


@app.command()
def list_deployments():
    """List all deployments."""
    async def _list():
        async with get_client() as client:
            deployments = await client.read_deployments()
            
            if not deployments:
                typer.echo("No deployments found.")
                return
            
            typer.echo("\nExisting deployments:")
            for deployment in deployments:
                typer.echo(f"  - {deployment.name} (ID: {deployment.id})")
                typer.echo(f"    Flow: {deployment.flow_name}")
                typer.echo(f"    Work Pool: {deployment.work_pool_name}")
                if deployment.schedule:
                    typer.echo(f"    Schedule: {deployment.schedule}")
                typer.echo()
    
    asyncio.run(_list())


@app.command()
def delete_deployment(
    deployment_name: str = typer.Argument(..., help="Name of deployment to delete")
):
    """Delete a deployment."""
    async def _delete():
        async with get_client() as client:
            deployments = await client.read_deployments()
            
            target_deployment = None
            for deployment in deployments:
                if deployment.name == deployment_name:
                    target_deployment = deployment
                    break
            
            if not target_deployment:
                typer.echo(f"Deployment '{deployment_name}' not found.")
                raise typer.Exit(1)
            
            await client.delete_deployment(target_deployment.id)
            typer.echo(f"Deleted deployment: {deployment_name}")
    
    asyncio.run(_delete())


if __name__ == "__main__":
    app()
