"""Example Prefect tasks for data processing and validation."""

from typing import Any, Dict
from prefect import task
from ..utils.logging import get_logger

logger = get_logger(__name__)


@task(name="process-data", retries=3, retry_delay_seconds=10)
def process_data(raw_data: str) -> Dict[str, Any]:
    """
    Process raw input data into structured format.
    
    Args:
        raw_data: Raw input data string
        
    Returns:
        Processed data dictionary
    """
    logger.info("Processing raw data", data_length=len(raw_data))
    
    try:
        # Example processing logic
        processed = {
            "original": raw_data,
            "length": len(raw_data),
            "uppercase": raw_data.upper(),
            "word_count": len(raw_data.split()),
            "processed_at": "2024-01-01T00:00:00Z"  # In real implementation, use datetime.utcnow()
        }
        
        logger.info("Data processing successful", processed_items=len(processed))
        return processed
        
    except Exception as e:
        logger.error("Data processing failed", error=str(e))
        raise


@task(name="validate-results", retries=2)
def validate_results(results: Any) -> Dict[str, bool]:
    """
    Validate analysis results for quality and completeness.
    
    Args:
        results: Results from analysis to validate
        
    Returns:
        Validation status dictionary
    """
    logger.info("Validating analysis results")
    
    validation = {
        "has_results": results is not None,
        "is_non_empty": bool(results) if results else False,
        "has_expected_structure": False,
        "quality_check_passed": False
    }
    
    try:
        # Example validation logic
        if isinstance(results, dict):
            validation["has_expected_structure"] = True
            validation["quality_check_passed"] = len(str(results)) > 10
        elif isinstance(results, str):
            validation["quality_check_passed"] = len(results) > 5
        
        logger.info("Validation completed", validation=validation)
        return validation
        
    except Exception as e:
        logger.error("Validation failed", error=str(e))
        raise


@task(name="send-notification")
def send_notification(message: str, recipient: str = "admin@company.com") -> bool:
    """
    Send notification about flow completion or errors.
    
    Args:
        message: Notification message
        recipient: Email recipient
        
    Returns:
        Success status
    """
    logger.info("Sending notification", recipient=recipient, message=message)
    
    # In real implementation, integrate with email service
    # Example: send email, Slack message, etc.
    
    logger.info("Notification sent successfully")
    return True


@task(name="save-results")
def save_results(results: Dict[str, Any], destination: str = "local") -> str:
    """
    Save flow results to specified destination.
    
    Args:
        results: Results to save
        destination: Storage destination (local, s3, database, etc.)
        
    Returns:
        Storage location or identifier
    """
    logger.info("Saving results", destination=destination, result_size=len(str(results)))
    
    try:
        # Example storage logic
        if destination == "local":
            # Save to local file
            location = f"/tmp/results_{hash(str(results))}.json"
        elif destination == "s3":
            # Save to S3 bucket
            location = f"s3://bucket/results/{hash(str(results))}.json"
        else:
            location = f"unknown://{destination}"
        
        logger.info("Results saved successfully", location=location)
        return location
        
    except Exception as e:
        logger.error("Failed to save results", error=str(e))
        raise
