"""Customer Prefect Flows - Workflow automation with CrewAI and LangChain using Prefect 3.x."""

__version__ = "1.0.0"
__author__ = "Your Team"
__email__ = "team@company.com"

# Configure logging on import
from .utils.logging import configure_logging

configure_logging()

# Export main components
from .config import get_settings
from .flows.example_flow import example_analysis_flow
from .agents.example_crew import create_analysis_crew

__all__ = [
    "get_settings",
    "example_analysis_flow", 
    "create_analysis_crew",
]
