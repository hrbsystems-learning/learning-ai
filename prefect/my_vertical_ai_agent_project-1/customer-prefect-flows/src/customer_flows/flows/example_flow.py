"""Example Prefect 3.x flow demonstrating CrewAI and LangChain integration."""

from typing import Any, Dict

from prefect import flow, task
from prefect.transactions import transaction

from ..agents.example_crew import create_analysis_crew
from ..config import get_settings
from ..utils.logging import bind_flow_context, get_logger

logger = get_logger(__name__)
settings = get_settings()


@task(
    name="process-input-data",
    description="Process raw input data into structured format",
    retries=3,
    retry_delay_seconds=10,
)
def process_data(raw_data: str) -> Dict[str, Any]:
    """
    Process raw input data into structured format.
    
    Args:
        raw_data: Raw input data string
        
    Returns:
        Processed data dictionary
    """
    task_logger = bind_flow_context(logger, task="process_data", data_length=len(raw_data))
    task_logger.info("Processing raw data")
    
    try:
        # Example processing logic with enhanced structure for Prefect 3
        processed = {
            "original": raw_data,
            "length": len(raw_data),
            "uppercase": raw_data.upper(),
            "lowercase": raw_data.lower(),
            "word_count": len(raw_data.split()),
            "character_count": len(raw_data.replace(" ", "")),
            "processed_at": "2024-01-01T00:00:00Z",  # In real implementation, use datetime.utcnow()
            "metadata": {
                "processor": "example_processor",
                "version": "1.0.0"
            }
        }
        
        task_logger.info("Data processing successful", processed_items=len(processed))
        return processed
        
    except Exception as e:
        task_logger.error("Data processing failed", error=str(e))
        raise


@task(
    name="run-crew-analysis",
    description="Execute CrewAI analysis on processed data",
    retries=2,
    retry_delay_seconds=30,
)
def run_crew_analysis(processed_data: Dict[str, Any]) -> Any:
    """
    Run CrewAI analysis on processed data.
    
    Args:
        processed_data: Previously processed data
        
    Returns:
        Analysis results from CrewAI
    """
    task_logger = bind_flow_context(logger, task="crew_analysis")
    task_logger.info("Starting CrewAI analysis")
    
    try:
        # Create and run CrewAI analysis
        crew = create_analysis_crew()
        analysis_result = crew.kickoff({"data": processed_data})
        
        task_logger.info("CrewAI analysis completed successfully")
        return analysis_result
        
    except Exception as e:
        task_logger.error("CrewAI analysis failed", error=str(e))
        raise


@task(
    name="validate-analysis-results",
    description="Validate analysis results for quality and completeness",
    retries=2,
)
def validate_results(results: Any) -> Dict[str, bool]:
    """
    Validate analysis results for quality and completeness.
    
    Args:
        results: Results from analysis to validate
        
    Returns:
        Validation status dictionary
    """
    task_logger = bind_flow_context(logger, task="validation")
    task_logger.info("Validating analysis results")
    
    validation = {
        "has_results": results is not None,
        "is_non_empty": bool(results) if results else False,
        "has_expected_structure": False,
        "quality_check_passed": False,
        "completeness_check": False,
    }
    
    try:
        # Enhanced validation logic for Prefect 3
        if isinstance(results, dict):
            validation["has_expected_structure"] = True
            validation["quality_check_passed"] = len(str(results)) > 10
            validation["completeness_check"] = all(
                key in results for key in ["data", "analysis"] if isinstance(results, dict)
            )
        elif isinstance(results, str):
            validation["quality_check_passed"] = len(results) > 5
            validation["completeness_check"] = len(results.split()) > 1
        
        task_logger.info("Validation completed", validation=validation)
        return validation
        
    except Exception as e:
        task_logger.error("Validation failed", error=str(e))
        raise


@task(
    name="save-results-to-storage",
    description="Save flow results to configured storage",
    retries=2,
)
def save_results(results: Dict[str, Any], validation: Dict[str, bool]) -> str:
    """
    Save flow results to configured storage.
    
    Args:
        results: Final results to save
        validation: Validation results
        
    Returns:
        Storage location identifier
    """
    task_logger = bind_flow_context(logger, task="save_results")
    task_logger.info("Saving results to storage")
    
    try:
        # Enhanced storage logic with validation
        if not validation.get("quality_check_passed", False):
            raise ValueError("Results did not pass quality validation")
        
        final_results = {
            "results": results,
            "validation": validation,
            "metadata": {
                "saved_at": "2024-01-01T00:00:00Z",
                "version": "1.0.0",
                "flow_name": "example-analysis-flow"
            }
        }
        
        # Example storage logic (replace with actual storage implementation)
        storage_id = f"results_{hash(str(final_results))}"
        location = f"storage://customer-flows/{storage_id}.json"
        
        task_logger.info("Results saved successfully", location=location)
        return location
        
    except Exception as e:
        task_logger.error("Failed to save results", error=str(e))
        raise


@flow(
    name="example-analysis-flow",
    description="Example flow using CrewAI and LangChain with Prefect 3 best practices",
    version="1.0.0",
    timeout_seconds=3600,
)
def example_analysis_flow(input_data: str, save_results_flag: bool = True) -> Dict[str, Any]:
    """
    Example flow that processes data using CrewAI agents and LangChain.
    
    This flow demonstrates Prefect 3 best practices including:
    - Proper task decomposition
    - Transaction management
    - Enhanced error handling
    - Structured logging
    - Result validation and storage
    
    Args:
        input_data: Raw input data to process
        save_results_flag: Whether to save results to storage
        
    Returns:
        Dictionary containing processing results and analysis
    """
    flow_logger = bind_flow_context(
        logger, 
        flow_name="example-analysis-flow",
        input_data_length=len(input_data)
    )
    flow_logger.info("Starting example analysis flow")
    
    try:
        # Use transactions for better error handling and rollback capabilities
        with transaction():
            # Step 1: Process the input data
            processed_data = process_data(input_data)
            flow_logger.info("Data processing step completed")
            
            # Step 2: Run CrewAI analysis
            analysis_result = run_crew_analysis(processed_data)
            flow_logger.info("CrewAI analysis step completed")
            
            # Step 3: Validate results
            validation_result = validate_results(analysis_result)
            flow_logger.info("Validation step completed")
            
            # Step 4: Optionally save results
            storage_location = None
            if save_results_flag:
                final_results = {
                    "processed_data": processed_data,
                    "analysis": analysis_result,
                    "validation": validation_result,
                }
                storage_location = save_results(final_results, validation_result)
                flow_logger.info("Results storage step completed")
            
            # Compile final flow result
            flow_result = {
                "processed_data": processed_data,
                "analysis": analysis_result,
                "validation": validation_result,
                "storage_location": storage_location,
                "status": "completed",
                "flow_metadata": {
                    "flow_name": "example-analysis-flow",
                    "version": "1.0.0",
                    "completed_at": "2024-01-01T00:00:00Z"
                }
            }
            
            flow_logger.info("Flow completed successfully", result_keys=list(flow_result.keys()))
            return flow_result
            
    except Exception as e:
        flow_logger.error("Flow execution failed", error=str(e), error_type=type(e).__name__)
        raise


if __name__ == "__main__":
    # Example usage with enhanced configuration
    from ..utils.logging import configure_logging
    
    # Configure logging
    configure_logging()
    
    # Run the flow
    result = example_analysis_flow("Sample data for analysis with Prefect 3")
    print(f"Flow result: {result}")
