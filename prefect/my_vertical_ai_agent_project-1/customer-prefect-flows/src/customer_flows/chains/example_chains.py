"""Example LangChain chains for text processing and analysis."""

from typing import Any, Dict, List
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import BaseOutputParser
from config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class StructuredOutputParser(BaseOutputParser):
    """Custom parser for structured output."""
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse LLM output into structured format."""
        try:
            # Simple structured parsing logic
            lines = text.strip().split('\n')
            result = {}
            current_section = None
            
            for line in lines:
                if line.startswith('##'):
                    current_section = line.replace('##', '').strip().lower().replace(' ', '_')
                    result[current_section] = []
                elif current_section and line.strip():
                    result[current_section].append(line.strip())
            
            return result
        except Exception as e:
            logger.error("Failed to parse output", error=str(e))
            return {"raw_output": text}


def create_analysis_chain() -> LLMChain:
    """
    Create a LangChain for data analysis.
    
    Returns:
        Configured LLMChain for analysis tasks
    """
    logger.info("Creating analysis chain")
    
    llm = ChatOpenAI(
        model="gpt-4",
        openai_api_key=settings.openai_api_key,
        temperature=0.1
    )
    
    prompt = PromptTemplate(
        input_variables=["data", "analysis_type"],
        template="""
        You are a data analyst. Analyze the following data and provide insights.
        
        Data: {data}
        Analysis Type: {analysis_type}
        
        Please provide your analysis in the following format:
        
        ## Summary
        Brief overview of the data and key findings
        
        ## Key Insights
        List the most important insights discovered
        
        ## Recommendations
        Actionable recommendations based on the analysis
        
        ## Potential Issues
        Any concerns or limitations identified
        
        Analysis:
        """
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=StructuredOutputParser(),
        verbose=True
    )
    
    logger.info("Analysis chain created successfully")
    return chain


def create_summarization_chain() -> LLMChain:
    """
    Create a LangChain for text summarization.
    
    Returns:
        Configured LLMChain for summarization tasks
    """
    logger.info("Creating summarization chain")
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",  # Using faster model for summarization
        openai_api_key=settings.openai_api_key,
        temperature=0.3
    )
    
    prompt = PromptTemplate(
        input_variables=["text", "max_length"],
        template="""
        Please summarize the following text. Keep the summary concise but comprehensive,
        capturing all key points. Maximum length: {max_length} words.
        
        Text to summarize:
        {text}
        
        Summary:
        """
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True
    )
    
    logger.info("Summarization chain created successfully")
    return chain


def create_classification_chain() -> LLMChain:
    """
    Create a LangChain for text classification.
    
    Returns:
        Configured LLMChain for classification tasks
    """
    logger.info("Creating classification chain")
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_key=settings.openai_api_key,
        temperature=0.1
    )
    
    prompt = PromptTemplate(
        input_variables=["text", "categories"],
        template="""
        Classify the following text into one of the provided categories.
        Provide your reasoning for the classification.
        
        Text: {text}
        
        Available Categories: {categories}
        
        Please respond in this format:
        ## Classification
        [Selected category]
        
        ## Confidence
        [Confidence level from 1-10]
        
        ## Reasoning
        [Explanation for your classification decision]
        
        Response:
        """
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=StructuredOutputParser(),
        verbose=True
    )
    
    logger.info("Classification chain created successfully")
    return chain


def create_qa_chain() -> LLMChain:
    """
    Create a LangChain for question answering.
    
    Returns:
        Configured LLMChain for Q&A tasks
    """
    logger.info("Creating Q&A chain")
    
    llm = ChatOpenAI(
        model="gpt-4",
        openai_api_key=settings.openai_api_key,
        temperature=0.2
    )
    
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        Answer the question based on the provided context. Be accurate and concise.
        If the answer cannot be determined from the context, say so clearly.
        
        Context: {context}
        
        Question: {question}
        
        Answer:
        """
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True
    )
    
    logger.info("Q&A chain created successfully")
    return chain


def create_extraction_chain() -> LLMChain:
    """
    Create a LangChain for information extraction.
    
    Returns:
        Configured LLMChain for extraction tasks
    """
    logger.info("Creating extraction chain")
    
    llm = ChatOpenAI(
        model="gpt-4",
        openai_api_key=settings.openai_api_key,
        temperature=0.1
    )
    
    prompt = PromptTemplate(
        input_variables=["text", "entities"],
        template="""
        Extract the specified entities from the following text.
        For each entity found, provide the exact text and its context.
        
        Text: {text}
        
        Entities to extract: {entities}
        
        Please format your response as:
        ## Extracted Entities
        [List each found entity with its context]
        
        ## Summary
        [Brief summary of extraction results]
        
        Response:
        """
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=StructuredOutputParser(),
        verbose=True
    )
    
    logger.info("Extraction chain created successfully")
    return chain


# Utility function to run chains with error handling
def run_chain_safely(chain: LLMChain, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a LangChain with error handling and logging.
    
    Args:
        chain: The LangChain to run
        inputs: Input parameters for the chain
        
    Returns:
        Chain output or error information
    """
    try:
        logger.info("Running chain", inputs=inputs)
        result = chain.run(**inputs)
        logger.info("Chain execution successful")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error("Chain execution failed", error=str(e))
        return {"success": False, "error": str(e)}
