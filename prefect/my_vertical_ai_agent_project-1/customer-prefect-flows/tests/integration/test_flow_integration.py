"""Integration tests for complete flow execution."""

import pytest
from unittest.mock import patch

from src.customer_flows.flows.example_flow import example_analysis_flow


class TestFlowIntegration:
    """Integration tests for complete flows."""
    
    @patch("langchain_openai.ChatOpenAI")
    @patch("crewai.Crew")
    def test_example_flow_end_to_end(self, mock_crew_class, mock_openai):
        """Test complete flow execution with mocked external services."""
        # Setup OpenAI mock
        mock_llm = mock_openai.return_value
        mock_llm.run.return_value = "Mocked LLM response"
        
        # Setup CrewAI mock
        mock_crew = mock_crew_class.return_value
        mock_crew.kickoff.return_value = {
            "analysis": "Comprehensive analysis of the provided data",
            "insights": ["Key insight 1", "Key insight 2"],
            "confidence": 0.85
        }
        
        # Run the flow
        input_data = "Sample data for comprehensive testing"
        result = example_analysis_flow(input_data)
        
        # Verify flow completion
        assert result["status"] == "completed"
        assert "processed_data" in result
        assert "analysis" in result
        assert "validation" in result
        
        # Verify processed data structure
        processed = result["processed_data"]
        assert processed["original"] == input_data
        assert processed["length"] == len(input_data)
        assert processed["word_count"] == len(input_data.split())
        
        # Verify analysis was performed
        analysis = result["analysis"]
        assert "analysis" in analysis
        assert "confidence" in analysis
        
        # Verify validation was performed
        validation = result["validation"]
        assert validation["has_results"] is True
        assert validation["is_non_empty"] is True
    
    @patch("langchain_openai.ChatOpenAI")
    @patch("crewai.Crew")
    def test_flow_with_empty_input(self, mock_crew_class, mock_openai):
        """Test flow behavior with empty input."""
        # Setup mocks
        mock_openai.return_value.run.return_value = "Analysis of empty data"
        mock_crew_class.return_value.kickoff.return_value = "Empty data analysis"
        
        # Run flow with empty input
        result = example_analysis_flow("")
        
        # Verify flow handles empty input gracefully
        assert result["status"] == "completed"
        assert result["processed_data"]["original"] == ""
        assert result["processed_data"]["length"] == 0
    
    @patch("langchain_openai.ChatOpenAI")
    @patch("crewai.Crew")
    def test_flow_with_large_input(self, mock_crew_class, mock_openai):
        """Test flow behavior with large input data."""
        # Setup mocks
        mock_openai.return_value.run.return_value = "Analysis of large dataset"
        mock_crew_class.return_value.kickoff.return_value = "Large data analysis"
        
        # Create large input data
        large_input = "This is a test. " * 1000  # 15000+ characters
        
        # Run flow
        result = example_analysis_flow(large_input)
        
        # Verify flow handles large input
        assert result["status"] == "completed"
        assert result["processed_data"]["length"] == len(large_input)
        assert result["processed_data"]["word_count"] == len(large_input.split())
    
    def test_flow_data_processing_pipeline(self):
        """Test the data processing pipeline without external services."""
        from src.customer_flows.tasks.example_tasks import process_data, validate_results
        
        # Test data processing
        input_data = "Integration test data processing"
        processed = process_data(input_data)
        
        # Verify processing results
        assert processed["original"] == input_data
        assert processed["uppercase"] == input_data.upper()
        assert processed["word_count"] == 4
        
        # Test validation
        validation = validate_results(processed)
        
        # Verify validation results
        assert validation["has_results"] is True
        assert validation["is_non_empty"] is True
        assert validation["has_expected_structure"] is True
        assert validation["quality_check_passed"] is True
