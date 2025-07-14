"""Prefect 3.x deployment configurations for customer flows."""

import os
from pathlib import Path
from typing import Dict, List, Optional

from prefect import flow
from prefect.client.schemas.schedules import CronSchedule, IntervalSchedule
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule as ServerIntervalSchedule

# Import flows
from src.customer_flows.flows.example_flow import example_analysis_flow
from src.customer_flows.config import get_settings

settings = get_settings()


def create_example_flow_deployment(
    environment: str = "development",
    work_pool_name: str = "default",
    schedule: Optional[str] = None,
) -> Deployment:
    """
    Create deployment for the example analysis flow.
    
    Args:
        environment: Deployment environment (development, staging, production)
        work_pool_name: Prefect work pool name
        schedule: Optional cron schedule string
        
    Returns:
        Configured Deployment object
    """
    
    # Configure deployment parameters based on environment
    deployment_config = {
        "development": {
            "version": "dev",
            "description": "Development deployment of example analysis flow",
            "tags": ["development", "example", "crewai"],
            "parameters": {
                "save_results_flag": False,  # Don't save results in dev
            },
        },
        "staging": {
            "version": "staging",
            "description": "Staging deployment of example analysis flow",
            "tags": ["staging", "example", "crewai"],
            "parameters": {
                "save_results_flag": True,
            },
        },
        "production": {
            "version": "1.0.0",
            "description": "Production deployment of example analysis flow",
            "tags": ["production", "example", "crewai"],
            "parameters": {
                "save_results_flag": True,
            },
        },
    }
    
    config = deployment_config.get(environment, deployment_config["development"])
    
    # Create schedule if provided
    flow_schedule = None
    if schedule:
        if schedule.startswith("cron:"):
            cron_expression = schedule.replace("cron:", "")
            flow_schedule = CronSchedule(cron=cron_expression)
        elif schedule.startswith("interval:"):
            interval_seconds = int(schedule.replace("interval:", ""))
            flow_schedule = IntervalSchedule(interval=interval_seconds)
    
    # Create deployment
    deployment = Deployment(
        name=f"example-analysis-{environment}",
        flow=example_analysis_flow,
        work_pool_name=work_pool_name,
        schedule=flow_schedule,
        version=config["version"],
        description=config["description"],
        tags=config["tags"],
        parameters=config["parameters"],
        # Prefect 3.x specific configurations
        enforce_parameter_schema=True,
        # Environment variables for the deployment
        job_variables={
            "env": {
                "ENVIRONMENT": environment,
                "PREFECT_API_URL": settings.prefect_api_url,
                "OPENAI_API_KEY": settings.openai_api_key,
                "LANGCHAIN_API_KEY": settings.langchain_api_key,
                "LANGCHAIN_PROJECT": settings.langchain_project,
                "LANGCHAIN_TRACING_V2": str(settings.langchain_tracing_v2),
            }
        },
    )
    
    return deployment


def create_all_deployments(
    environments: List[str] = None,
    work_pool_name: str = "default",
    schedules: Optional[Dict[str, str]] = None,
) -> List[Deployment]:
    """
    Create deployments for all environments.
    
    Args:
        environments: List of environments to deploy to
        work_pool_name: Prefect work pool name
        schedules: Environment-specific schedules
        
    Returns:
        List of configured Deployment objects
    """
    if environments is None:
        environments = ["development", "staging", "production"]
    
    schedules = schedules or {}
    deployments = []
    
    for env in environments:
        schedule = schedules.get(env)
        deployment = create_example_flow_deployment(
            environment=env,
            work_pool_name=work_pool_name,
            schedule=schedule,
        )
        deployments.append(deployment)
    
    return deployments


def deploy_flows(
    environments: List[str] = None,
    work_pool_name: str = "default",
    schedules: Optional[Dict[str, str]] = None,
    dry_run: bool = False,
) -> Dict[str, str]:
    """
    Deploy flows to Prefect server/cloud.
    
    Args:
        environments: List of environments to deploy to
        work_pool_name: Prefect work pool name
        schedules: Environment-specific schedules
        dry_run: If True, only validate deployments without deploying
        
    Returns:
        Dictionary mapping environment to deployment ID
    """
    deployments = create_all_deployments(environments, work_pool_name, schedules)
    deployment_ids = {}
    
    for deployment in deployments:
        try:
            if dry_run:
                print(f"[DRY RUN] Would deploy: {deployment.name}")
                print(f"  Flow: {deployment.flow.name}")
                print(f"  Work Pool: {deployment.work_pool_name}")
                print(f"  Tags: {deployment.tags}")
                print(f"  Schedule: {deployment.schedule}")
                print()
                deployment_ids[deployment.name] = "dry-run-id"
            else:
                # Deploy the flow
                deployment_id = deployment.deploy()
                deployment_ids[deployment.name] = deployment_id
                print(f"✓ Deployed {deployment.name} with ID: {deployment_id}")
                
        except Exception as e:
            print(f"✗ Failed to deploy {deployment.name}: {e}")
            raise
    
    return deployment_ids


# Prefect 3.x deployment script
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Prefect flows")
    parser.add_argument(
        "--environments",
        nargs="+",
        default=["development"],
        help="Environments to deploy to",
    )
    parser.add_argument(
        "--work-pool",
        default="default",
        help="Prefect work pool name",
    )
    parser.add_argument(
        "--schedule-dev",
        help="Schedule for development environment (e.g., 'cron:0 9 * * *')",
    )
    parser.add_argument(
        "--schedule-staging",
        help="Schedule for staging environment",
    )
    parser.add_argument(
        "--schedule-prod",
        help="Schedule for production environment",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deployed without actually deploying",
    )
    
    args = parser.parse_args()
    
    # Prepare schedules
    schedules = {}
    if args.schedule_dev:
        schedules["development"] = args.schedule_dev
    if args.schedule_staging:
        schedules["staging"] = args.schedule_staging
    if args.schedule_prod:
        schedules["production"] = args.schedule_prod
    
    # Deploy flows
    print("Deploying Prefect flows...")
    print(f"Environments: {args.environments}")
    print(f"Work Pool: {args.work_pool}")
    print(f"Schedules: {schedules}")
    print()
    
    deployment_ids = deploy_flows(
        environments=args.environments,
        work_pool_name=args.work_pool,
        schedules=schedules,
        dry_run=args.dry_run,
    )
    
    print("\nDeployment Summary:")
    for name, deployment_id in deployment_ids.items():
        print(f"  {name}: {deployment_id}")
