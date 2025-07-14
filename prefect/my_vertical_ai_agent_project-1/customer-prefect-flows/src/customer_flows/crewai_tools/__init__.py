"""
CrewAI Tools for Customer Prefect Flows

This package contains all the tools used by CrewAI agents in the customer flows.
Tools are organized by category:
- data: Data processing and manipulation tools
- communication: Email, messaging, and notification tools  
- web: Web scraping, API calls, and browser automation tools
- analysis: Data analysis, reporting, and visualization tools
- storage: File handling, database operations, and data persistence tools
"""

from .web import *
from .data import *
from .communication import *
from .analysis import *
from .storage import *

__all__ = [
    # Web tools
    "WebScrapingTool",
    "APICallTool",
    "BrowserTool",
    
    # Data tools
    "DataProcessingTool",
    "CSVTool",
    "JSONTool",
    
    # Communication tools
    "EmailTool",
    "SlackTool",
    "NotificationTool",
    
    # Analysis tools
    "DataAnalysisTool",
    "ReportingTool",
    "VisualizationTool",
    
    # Storage tools
    "FileStorageTool",
    "DatabaseTool",
    "CloudStorageTool",
]
