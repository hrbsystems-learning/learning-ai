"""Unit tests for Prefect tasks."""

import pytest
from unittest.mock import patch, Mock

from src.customer_flows.tasks.example_tasks import (
    process_data,
    validate_results,
    send_notification,
    save_results
)


class TestProcessData:
    """Test process_data task."""
    
    def test_process_data_success(self):
        """Test successful data processing."""
        raw_data = "Hello World Test"
        
        result = process_data(raw_data)
        
        assert result["original"] == raw_data
        assert result["length"] == len(raw_data)
        assert result["uppercase"] == raw_data.upper()
        assert result["word_count"] == 3
        assert "processed_at" in result
    
    def test_process_data_empty_string(self):
        """Test processing empty string."""
        raw_data = ""
        
        result = process_data(raw_data)
        
        assert result["original"] == ""
        assert result["length"] == 0
        assert result["word_count"] == 1  # split() on empty string returns ['']
    
    def test_process_data_with_special_chars(self):
        """Test processing text with special characters."""
        raw_data = "Hello, World! 123 @#$"
        
        result = process_data(raw_data)
        
        assert result["original"] == raw_data
        assert result["uppercase"] == "HELLO, WORLD! 123 @#$"
        assert result["word_count"] == 3


class TestValidateResults:
    """Test validate_results task."""
    
    def test_validate_dict_results(self):
        """Test validation of dictionary results."""
        results = {"key": "value", "data": [1, 2, 3]}
        
        validation = validate_results(results)
        
        assert validation["has_results"] is True
        assert validation["is_non_empty"] is True
        assert validation["has_expected_structure"] is True
        assert validation["quality_check_passed"] is True
    
    def test_validate_string_results(self):
        """Test validation of string results."""
        results = "This is a test result"
        
        validation = validate_results(results)
        
        assert validation["has_results"] is True
        assert validation["is_non_empty"] is True
        assert validation["has_expected_structure"] is False
        assert validation["quality_check_passed"] is True
    
    def test_validate_none_results(self):
        """Test validation of None results."""
        results = None
        
        validation = validate_results(results)
        
        assert validation["has_results"] is False
        assert validation["is_non_empty"] is False
        assert validation["has_expected_structure"] is False
        assert validation["quality_check_passed"] is False
    
    def test_validate_empty_results(self):
        """Test validation of empty results."""
        results = {}
        
        validation = validate_results(results)
        
        assert validation["has_results"] is True
        assert validation["is_non_empty"] is False
        assert validation["has_expected_structure"] is True
        assert validation["quality_check_passed"] is False


class TestSendNotification:
    """Test send_notification task."""
    
    @patch("src.customer_flows.tasks.example_tasks.logger")
    def test_send_notification_success(self, mock_logger):
        """Test successful notification sending."""
        message = "Test notification message"
        recipient = "test@example.com"
        
        result = send_notification(message, recipient)
        
        assert result is True
        mock_logger.info.assert_called()
    
    @patch("src.customer_flows.tasks.example_tasks.logger")
    def test_send_notification_default_recipient(self, mock_logger):
        """Test notification with default recipient."""
        message = "Test message"
        
        result = send_notification(message)
        
        assert result is True
        mock_logger.info.assert_called()


class TestSaveResults:
    """Test save_results task."""
    
    @patch("src.customer_flows.tasks.example_tasks.logger")
    def test_save_results_local(self, mock_logger):
        """Test saving results locally."""
        results = {"test": "data"}
        
        location = save_results(results, "local")
        
        assert location.startswith("/tmp/results_")
        assert location.endswith(".json")
        mock_logger.info.assert_called()
    
    @patch("src.customer_flows.tasks.example_tasks.logger")
    def test_save_results_s3(self, mock_logger):
        """Test saving results to S3."""
        results = {"test": "data"}
        
        location = save_results(results, "s3")
        
        assert location.startswith("s3://bucket/results/")
        assert location.endswith(".json")
        mock_logger.info.assert_called()
    
    @patch("src.customer_flows.tasks.example_tasks.logger")
    def test_save_results_unknown_destination(self, mock_logger):
        """Test saving results to unknown destination."""
        results = {"test": "data"}
        
        location = save_results(results, "unknown")
        
        assert location == "unknown://unknown"
        mock_logger.info.assert_called()
