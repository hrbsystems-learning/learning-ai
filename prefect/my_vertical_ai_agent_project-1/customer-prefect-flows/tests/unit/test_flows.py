"""Unit tests for Prefect flows."""

import pytest
from unittest.mock import patch, Mock

from src.customer_flows.flows.example_flow import example_analysis_flow


class TestExampleAnalysisFlow:
    """Test example_analysis_flow."""
    
    @patch("src.customer_flows.flows.example_flow.create_analysis_crew")
    @patch("src.customer_flows.flows.example_flow.validate_results")
    @patch("src.customer_flows.flows.example_flow.process_data")
    def test_example_flow_success(self, mock_process_data, mock_validate_results, mock_create_crew):
        """Test successful flow execution."""
        # Setup mocks
        mock_process_data.return_value = {"processed": "test data"}
        mock_validate_results.return_value = {"status": "valid"}
        
        mock_crew = Mock()
        mock_crew.kickoff.return_value = {"analysis": "test analysis"}
        mock_create_crew.return_value = mock_crew
        
        # Run flow
        input_data = "test input"
        result = example_analysis_flow(input_data)
        
        # Assertions
        assert result["status"] == "completed"
        assert "processed_data" in result
        assert "analysis" in result
        assert "validation" in result
        
        # Verify task calls
        mock_process_data.assert_called_once_with(input_data)
        mock_validate_results.assert_called_once()
        mock_crew.kickoff.assert_called_once()
    
    @patch("src.customer_flows.flows.example_flow.create_analysis_crew")
    @patch("src.customer_flows.flows.example_flow.validate_results")
    @patch("src.customer_flows.flows.example_flow.process_data")
    def test_example_flow_with_different_input(self, mock_process_data, mock_validate_results, mock_create_crew):
        """Test flow with different input data."""
        # Setup mocks
        mock_process_data.return_value = {"processed": "different data"}
        mock_validate_results.return_value = {"status": "valid"}
        
        mock_crew = Mock()
        mock_crew.kickoff.return_value = {"analysis": "different analysis"}
        mock_create_crew.return_value = mock_crew
        
        # Run flow
        input_data = "completely different input data"
        result = example_analysis_flow(input_data)
        
        # Assertions
        assert result["status"] == "completed"
        assert result["processed_data"]["processed"] == "different data"
        assert result["analysis"]["analysis"] == "different analysis"
        
        # Verify correct input was passed
        mock_process_data.assert_called_once_with(input_data)
    
    @patch("src.customer_flows.flows.example_flow.create_analysis_crew")
    @patch("src.customer_flows.flows.example_flow.validate_results")
    @patch("src.customer_flows.flows.example_flow.process_data")
    @patch("src.customer_flows.flows.example_flow.logger")
    def test_example_flow_logging(self, mock_logger, mock_process_data, mock_validate_results, mock_create_crew):
        """Test that flow logs appropriately."""
        # Setup mocks
        mock_process_data.return_value = {"processed": "test"}
        mock_validate_results.return_value = {"status": "valid"}
        
        mock_crew = Mock()
        mock_crew.kickoff.return_value = {"analysis": "test"}
        mock_create_crew.return_value = mock_crew
        
        # Run flow
        example_analysis_flow("test input")
        
        # Verify logging calls
        assert mock_logger.info.call_count >= 4  # At least 4 log calls expected
        
        # Check specific log messages
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert "Starting example analysis flow" in log_calls
        assert "Flow completed successfully" in log_calls
