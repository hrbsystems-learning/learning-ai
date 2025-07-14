"""CrewAI agent configurations for customer flows with Prefect 3 integration."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from crewai import Agent, Crew, Task, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

from ..config import get_settings
from ..utils.logging import bind_flow_context, get_logger

logger = get_logger(__name__)
settings = get_settings()


class AgentManager:
    """Manages CrewAI agents with enhanced configuration and monitoring."""
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent manager.
        
        Args:
            llm_config: LLM configuration overrides
        """
        self.logger = bind_flow_context(logger, component="agent_manager")
        self.settings = get_settings()
        
        # Configure LLM with fallbacks
        default_config = {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        
        if llm_config:
            default_config.update(llm_config)
        
        try:
            self.llm = ChatOpenAI(
                openai_api_key=self.settings.openai_api_key,
                **default_config
            )
            self.logger.info("LLM initialized successfully", model=default_config["model"])
        except Exception as e:
            self.logger.error("Failed to initialize LLM", error=str(e))
            raise
    
    def create_data_analyst_agent(self) -> Agent:
        """Create a data analysis specialist agent."""
        return Agent(
            role="Data Analyst",
            goal="Analyze data comprehensively and extract meaningful insights",
            backstory="""You are an expert data analyst with years of experience in 
            extracting insights from various types of data. You excel at identifying 
            patterns, trends, and anomalies that others might miss. Your analytical 
            approach is both thorough and practical, always considering the business 
            context of your findings.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[DuckDuckGoSearchRun()] if self._tools_available() else [],
            max_iter=3,
            memory=True,
        )
    
    def create_insight_generator_agent(self) -> Agent:
        """Create an insight generation specialist agent."""
        return Agent(
            role="Insight Generator",
            goal="Transform raw analysis into actionable business insights",
            backstory="""You are a strategic thinker who specializes in translating 
            complex data analysis into clear, actionable business insights. You have 
            a talent for seeing the bigger picture and understanding how data-driven 
            findings can impact business decisions and outcomes.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=2,
            memory=True,
        )
    
    def create_quality_reviewer_agent(self) -> Agent:
        """Create a quality assurance specialist agent."""
        return Agent(
            role="Quality Reviewer",
            goal="Ensure analysis quality and validate findings",
            backstory="""You are a meticulous quality assurance specialist with 
            expertise in reviewing analytical work. You have a keen eye for 
            inconsistencies, logical gaps, and potential biases. Your role is to 
            ensure that all analysis meets high standards of accuracy and reliability.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=2,
            memory=True,
        )
    
    def _tools_available(self) -> bool:
        """Check if external tools are available and configured."""
        try:
            # Add logic to check tool availability
            return True
        except Exception:
            self.logger.warning("External tools not available, proceeding without tools")
            return False


def create_data_analysis_tasks(data: Dict[str, Any]) -> List[Task]:
    """
    Create a comprehensive set of analysis tasks.
    
    Args:
        data: Input data for analysis
        
    Returns:
        List of configured tasks
    """
    task_logger = bind_flow_context(logger, component="task_creator")
    task_logger.info("Creating data analysis tasks")
    
    # Task 1: Primary Data Analysis
    analysis_task = Task(
        description=f"""
        Perform a comprehensive analysis of the provided data:
        
        Data Summary:
        - Original content: {data.get('original', 'N/A')[:200]}...
        - Word count: {data.get('word_count', 'N/A')}
        - Character count: {data.get('character_count', 'N/A')}
        - Processing metadata: {data.get('metadata', {})}
        
        Your analysis should include:
        1. Content structure and organization assessment
        2. Key themes and topics identification
        3. Statistical analysis of text properties
        4. Pattern recognition and anomaly detection
        5. Contextual relevance evaluation
        
        Provide detailed findings with supporting evidence.
        """,
        expected_output="A comprehensive analysis report with key findings, patterns, and statistical insights.",
        agent=None,  # Will be assigned when creating the crew
    )
    
    # Task 2: Insight Generation
    insight_task = Task(
        description="""
        Based on the data analysis results, generate actionable business insights:
        
        1. Identify the top 3-5 most significant findings
        2. Explain the business implications of each finding
        3. Suggest specific actions or recommendations
        4. Assess potential risks and opportunities
        5. Prioritize insights by impact and feasibility
        
        Focus on practical, implementable recommendations.
        """,
        expected_output="A prioritized list of actionable business insights with clear recommendations and impact assessments.",
        agent=None,  # Will be assigned when creating the crew
    )
    
    # Task 3: Quality Review
    review_task = Task(
        description="""
        Review the analysis and insights for quality and accuracy:
        
        1. Verify the logical consistency of findings
        2. Check for potential biases or blind spots
        3. Validate the reasoning behind recommendations
        4. Assess the completeness of the analysis
        5. Identify any gaps or areas for improvement
        
        Provide a quality score (1-10) and detailed feedback.
        """,
        expected_output="A quality assessment report with scores, validation results, and improvement recommendations.",
        agent=None,  # Will be assigned when creating the crew
    )
    
    return [analysis_task, insight_task, review_task]


def create_analysis_crew(data: Optional[Dict[str, Any]] = None, crew_config: Optional[Dict[str, Any]] = None) -> Crew:
    """
    Create a comprehensive analysis crew with multiple specialized agents.
    
    Args:
        data: Input data for analysis (if None, will expect data in kickoff)
        crew_config: Crew configuration overrides
        
    Returns:
        Configured CrewAI crew
    """
    crew_logger = bind_flow_context(logger, component="crew_creator")
    crew_logger.info("Creating analysis crew")
    
    try:
        # Initialize agent manager
        agent_manager = AgentManager()
        
        # Create specialized agents
        data_analyst = agent_manager.create_data_analyst_agent()
        insight_generator = agent_manager.create_insight_generator_agent()
        quality_reviewer = agent_manager.create_quality_reviewer_agent()
        
        # Create tasks (will be customized based on actual data during execution)
        default_data = data or {
            "original": "Sample data",
            "word_count": 0,
            "character_count": 0,
            "metadata": {}
        }
        
        tasks = create_data_analysis_tasks(default_data)
        
        # Assign agents to tasks
        tasks[0].agent = data_analyst
        tasks[1].agent = insight_generator
        tasks[2].agent = quality_reviewer
        
        # Configure crew settings
        default_crew_config = {
            "process": Process.sequential,
            "verbose": True,
            "memory": True,
            "max_rpm": 10,
        }
        
        if crew_config:
            default_crew_config.update(crew_config)
        
        # Create the crew
        crew = Crew(
            agents=[data_analyst, insight_generator, quality_reviewer],
            tasks=tasks,
            process=default_crew_config["process"],
            verbose=default_crew_config["verbose"],
            memory=default_crew_config["memory"],
            max_rpm=default_crew_config.get("max_rpm"),
        )
        
        crew_logger.info(
            "Analysis crew created successfully",
            agents_count=len(crew.agents),
            tasks_count=len(crew.tasks),
            process=default_crew_config["process"]
        )
        
        return crew
        
    except Exception as e:
        crew_logger.error("Failed to create analysis crew", error=str(e))
        raise


def create_specialized_crew(
    crew_type: str, 
    data: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Crew:
    """
    Create specialized crews for different types of analysis.
    
    Args:
        crew_type: Type of crew to create ('analysis', 'research', 'validation', etc.)
        data: Input data for the crew
        config: Crew-specific configuration
        
    Returns:
        Configured specialized crew
    """
    crew_logger = bind_flow_context(logger, component="specialized_crew_creator", crew_type=crew_type)
    crew_logger.info("Creating specialized crew")
    
    if crew_type == "analysis":
        return create_analysis_crew(data, config)
    elif crew_type == "research":
        # Create research-focused crew
        return _create_research_crew(data, config)
    elif crew_type == "validation":
        # Create validation-focused crew
        return _create_validation_crew(data, config)
    else:
        raise ValueError(f"Unsupported crew type: {crew_type}")


def _create_research_crew(data: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> Crew:
    """Create a research-focused crew (placeholder for future implementation)."""
    # Implement research crew creation logic
    return create_analysis_crew(data, config)  # Fallback to analysis crew for now


def _create_validation_crew(data: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> Crew:
    """Create a validation-focused crew (placeholder for future implementation)."""
    # Implement validation crew creation logic
    return create_analysis_crew(data, config)  # Fallback to analysis crew for now


# Utility functions for crew management

def get_crew_metrics(crew: Crew) -> Dict[str, Any]:
    """
    Get performance metrics for a crew.
    
    Args:
        crew: The crew to analyze
        
    Returns:
        Dictionary containing crew metrics
    """
    return {
        "agents_count": len(crew.agents),
        "tasks_count": len(crew.tasks),
        "process_type": str(crew.process),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_crew_configuration(crew: Crew) -> Dict[str, Any]:
    """
    Validate crew configuration for potential issues.
    
    Args:
        crew: The crew to validate
        
    Returns:
        Validation results
    """
    validation_logger = bind_flow_context(logger, component="crew_validator")
    
    validation_results = {
        "is_valid": True,
        "warnings": [],
        "errors": [],
        "recommendations": [],
    }
    
    try:
        # Check agent configuration
        if not crew.agents:
            validation_results["errors"].append("No agents configured")
            validation_results["is_valid"] = False
        
        # Check task configuration
        if not crew.tasks:
            validation_results["errors"].append("No tasks configured")
            validation_results["is_valid"] = False
        
        # Check agent-task assignment
        unassigned_tasks = [task for task in crew.tasks if task.agent is None]
        if unassigned_tasks:
            validation_results["warnings"].append(f"Found {len(unassigned_tasks)} unassigned tasks")
        
        # Performance recommendations
        if len(crew.agents) > 5:
            validation_results["recommendations"].append("Consider reducing agent count for better performance")
        
        if len(crew.tasks) > 10:
            validation_results["recommendations"].append("Consider breaking down complex workflows")
        
        validation_logger.info("Crew validation completed", **validation_results)
        
    except Exception as e:
        validation_logger.error("Crew validation failed", error=str(e))
        validation_results["errors"].append(f"Validation error: {str(e)}")
        validation_results["is_valid"] = False
    
    return validation_results
