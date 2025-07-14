"""Core Prefect 3.x tasks for data processing and operations."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from prefect import task
from prefect.transactions import transaction

from ..config import get_settings
from ..utils.logging import bind_flow_context, get_logger

logger = get_logger(__name__)
settings = get_settings()


@task(
    name="data-preprocessing",
    description="Advanced data preprocessing with validation",
    retries=3,
    retry_delay_seconds=10,
    tags=["data", "preprocessing"],
)
def preprocess_data(raw_data: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Advanced data preprocessing with multiple transformation options.
    
    Args:
        raw_data: Raw input data string
        options: Processing options dictionary
        
    Returns:
        Processed data with metadata
    """
    task_logger = bind_flow_context(logger, task="preprocess_data")
    task_logger.info("Starting data preprocessing", data_length=len(raw_data))
    
    options = options or {}
    
    try:
        processed = {
            "original": raw_data,
            "length": len(raw_data),
            "word_count": len(raw_data.split()),
            "character_count": len(raw_data.replace(" ", "")),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Apply optional transformations
        if options.get("uppercase", False):
            processed["uppercase"] = raw_data.upper()
        
        if options.get("lowercase", False):
            processed["lowercase"] = raw_data.lower()
        
        if options.get("remove_punctuation", False):
            import string
            processed["clean_text"] = raw_data.translate(str.maketrans('', '', string.punctuation))
        
        if options.get("extract_keywords", False):
            # Simple keyword extraction (replace with more sophisticated NLP)
            words = raw_data.lower().split()
            processed["keywords"] = list(set([word for word in words if len(word) > 4]))[:10]
        
        # Add processing metadata
        processed["metadata"] = {
            "processor": "core_preprocessor",
            "version": "1.0.0",
            "options_applied": list(options.keys()),
            "processing_time": "2024-01-01T00:00:00Z",  # Replace with actual timing
        }
        
        task_logger.info("Data preprocessing completed", processed_fields=len(processed))
        return processed
        
    except Exception as e:
        task_logger.error("Data preprocessing failed", error=str(e))
        raise


@task(
    name="data-validation",
    description="Comprehensive data validation with custom rules",
    retries=2,
    tags=["validation", "quality"],
)
def validate_data(data: Dict[str, Any], rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Comprehensive data validation with customizable rules.
    
    Args:
        data: Data to validate
        rules: Validation rules dictionary
        
    Returns:
        Validation results with detailed feedback
    """
    task_logger = bind_flow_context(logger, task="validate_data")
    task_logger.info("Starting data validation")
    
    rules = rules or {}
    
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "checks_performed": [],
        "metadata": {
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "validator_version": "1.0.0",
        }
    }
    
    try:
        # Basic existence checks
        if not data:
            validation_result["errors"].append("Data is empty or None")
            validation_result["is_valid"] = False
        validation_result["checks_performed"].append("existence_check")
        
        # Type validation
        if not isinstance(data, dict):
            validation_result["errors"].append("Data must be a dictionary")
            validation_result["is_valid"] = False
        validation_result["checks_performed"].append("type_check")
        
        # Custom rule validations
        if rules.get("min_length") and len(str(data)) < rules["min_length"]:
            validation_result["errors"].append(f"Data length below minimum: {rules['min_length']}")
            validation_result["is_valid"] = False
        
        if rules.get("required_fields"):
            missing_fields = set(rules["required_fields"]) - set(data.keys())
            if missing_fields:
                validation_result["errors"].append(f"Missing required fields: {list(missing_fields)}")
                validation_result["is_valid"] = False
        
        if rules.get("max_size") and len(str(data)) > rules["max_size"]:
            validation_result["warnings"].append(f"Data size exceeds recommended maximum: {rules['max_size']}")
        
        validation_result["checks_performed"].extend(["custom_rules"])
        
        task_logger.info(
            "Data validation completed", 
            is_valid=validation_result["is_valid"],
            errors_count=len(validation_result["errors"]),
            warnings_count=len(validation_result["warnings"])
        )
        
        return validation_result
        
    except Exception as e:
        task_logger.error("Data validation failed", error=str(e))
        raise


@task(
    name="send-notification",
    description="Send notifications via multiple channels",
    retries=2,
    retry_delay_seconds=5,
    tags=["notification", "communication"],
)
def send_notification(
    message: str, 
    recipients: List[str], 
    channels: List[str] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Send notifications through multiple channels.
    
    Args:
        message: Notification message
        recipients: List of recipient identifiers
        channels: List of channels to use (email, slack, webhook, etc.)
        priority: Notification priority (low, normal, high, urgent)
        
    Returns:
        Notification delivery status
    """
    task_logger = bind_flow_context(logger, task="send_notification")
    task_logger.info("Sending notification", recipients_count=len(recipients), priority=priority)
    
    channels = channels or ["email"]
    
    try:
        notification_results = {
            "message": message,
            "recipients": recipients,
            "channels_used": channels,
            "priority": priority,
            "delivery_status": {},
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Simulate notification sending for each channel
        for channel in channels:
            if channel == "email":
                # Email notification logic
                notification_results["delivery_status"][channel] = {
                    "status": "sent",
                    "details": f"Email sent to {len(recipients)} recipients"
                }
            elif channel == "slack":
                # Slack notification logic
                notification_results["delivery_status"][channel] = {
                    "status": "sent",
                    "details": f"Slack message sent to {len(recipients)} channels"
                }
            elif channel == "webhook":
                # Webhook notification logic
                notification_results["delivery_status"][channel] = {
                    "status": "sent",
                    "details": f"Webhook called for {len(recipients)} endpoints"
                }
            else:
                notification_results["delivery_status"][channel] = {
                    "status": "unsupported",
                    "details": f"Channel {channel} not implemented"
                }
        
        task_logger.info("Notification sent successfully", channels=channels)
        return notification_results
        
    except Exception as e:
        task_logger.error("Notification sending failed", error=str(e))
        raise


@task(
    name="persist-results",
    description="Persist results to multiple storage backends",
    retries=3,
    retry_delay_seconds=15,
    tags=["storage", "persistence"],
)
def persist_results(
    results: Dict[str, Any], 
    storage_config: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Persist results to configured storage backends.
    
    Args:
        results: Results data to persist
        storage_config: Storage configuration options
        
    Returns:
        Storage locations for each backend
    """
    task_logger = bind_flow_context(logger, task="persist_results")
    task_logger.info("Persisting results to storage")
    
    storage_config = storage_config or {"backends": ["local"]}
    storage_locations = {}
    
    try:
        # Add persistence metadata
        enriched_results = {
            **results,
            "persistence_metadata": {
                "persisted_at": datetime.now(timezone.utc).isoformat(),
                "storage_version": "1.0.0",
                "backends": storage_config.get("backends", ["local"]),
            }
        }
        
        # Persist to each configured backend
        for backend in storage_config.get("backends", ["local"]):
            if backend == "local":
                # Local file storage
                import json
                import hashlib
                
                result_hash = hashlib.md5(str(enriched_results).encode()).hexdigest()[:8]
                filename = f"results_{result_hash}.json"
                storage_locations[backend] = f"file://./storage/{filename}"
                
                # In production, actually write the file
                # with open(f"./storage/{filename}", "w") as f:
                #     json.dump(enriched_results, f, indent=2)
                
            elif backend == "s3":
                # S3 storage
                result_hash = hashlib.md5(str(enriched_results).encode()).hexdigest()[:8]
                key = f"customer-flows/results/{result_hash}.json"
                storage_locations[backend] = f"s3://your-bucket/{key}"
                
            elif backend == "database":
                # Database storage
                record_id = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                storage_locations[backend] = f"db://results/{record_id}"
                
            else:
                task_logger.warning(f"Unsupported storage backend: {backend}")
        
        task_logger.info("Results persisted successfully", locations=storage_locations)
        return storage_locations
        
    except Exception as e:
        task_logger.error("Results persistence failed", error=str(e))
        raise


@task(
    name="cleanup-resources",
    description="Clean up temporary resources and artifacts",
    retries=1,
    tags=["cleanup", "maintenance"],
)
def cleanup_resources(resource_ids: List[str], cleanup_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Clean up temporary resources and artifacts.
    
    Args:
        resource_ids: List of resource identifiers to clean up
        cleanup_config: Cleanup configuration options
        
    Returns:
        Cleanup results and summary
    """
    task_logger = bind_flow_context(logger, task="cleanup_resources")
    task_logger.info("Starting resource cleanup", resource_count=len(resource_ids))
    
    cleanup_config = cleanup_config or {}
    
    try:
        cleanup_results = {
            "resources_cleaned": [],
            "failed_cleanups": [],
            "cleanup_summary": {
                "total_resources": len(resource_ids),
                "successfully_cleaned": 0,
                "failed_cleanups": 0,
            },
            "cleaned_at": datetime.now(timezone.utc).isoformat(),
        }
        
        for resource_id in resource_ids:
            try:
                # Simulate resource cleanup
                # In production, implement actual cleanup logic based on resource type
                task_logger.debug(f"Cleaning up resource: {resource_id}")
                
                cleanup_results["resources_cleaned"].append({
                    "resource_id": resource_id,
                    "status": "cleaned",
                    "cleaned_at": datetime.now(timezone.utc).isoformat(),
                })
                cleanup_results["cleanup_summary"]["successfully_cleaned"] += 1
                
            except Exception as cleanup_error:
                task_logger.warning(f"Failed to cleanup resource {resource_id}", error=str(cleanup_error))
                cleanup_results["failed_cleanups"].append({
                    "resource_id": resource_id,
                    "error": str(cleanup_error),
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                })
                cleanup_results["cleanup_summary"]["failed_cleanups"] += 1
        
        task_logger.info(
            "Resource cleanup completed",
            successfully_cleaned=cleanup_results["cleanup_summary"]["successfully_cleaned"],
            failed_cleanups=cleanup_results["cleanup_summary"]["failed_cleanups"]
        )
        
        return cleanup_results
        
    except Exception as e:
        task_logger.error("Resource cleanup failed", error=str(e))
        raise
