"""Web-related tools for CrewAI agents."""

import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import time

from crewai_tools import BaseTool
from pydantic import Field
import httpx
from bs4 import BeautifulSoup

from ..config import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class WebSearchTool(BaseTool):
    """Tool for searching the web using various search engines."""
    
    name: str = "web_search"
    description: str = (
        "Search the web for information on any topic. "
        "Useful for finding current information, news, research, and answers to questions. "
        "Input should be a search query string."
    )
    
    search_engine: str = Field(default="duckduckgo", description="Search engine to use")
    max_results: int = Field(default=10, description="Maximum number of results to return")
    
    def _run(self, query: str) -> str:
        """Execute web search and return results."""
        logger.info("Performing web search", query=query, engine=self.search_engine)
        
        try:
            if self.search_engine.lower() == "duckduckgo":
                return self._search_duckduckgo(query)
            else:
                return f"Search engine {self.search_engine} not implemented yet"
                
        except Exception as e:
            logger.error("Web search failed", error=str(e))
            return f"Search failed: {str(e)}"
    
    def _search_duckduckgo(self, query: str) -> str:
        """Search using DuckDuckGo."""
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
            
            if not results:
                return "No search results found."
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. **{result.get('title', 'No title')}**\n"
                    f"   URL: {result.get('href', 'No URL')}\n"
                    f"   Summary: {result.get('body', 'No summary')}\n"
                )
            
            return "\n".join(formatted_results)
            
        except ImportError:
            logger.warning("DuckDuckGo search not available, install duckduckgo-search")
            return "DuckDuckGo search not available. Please install duckduckgo-search package."
        except Exception as e:
            logger.error("DuckDuckGo search failed", error=str(e))
            return f"Search failed: {str(e)}"


class WebScrapingTool(BaseTool):
    """Tool for scraping content from web pages."""
    
    name: str = "web_scraping"
    description: str = (
        "Scrape and extract text content from web pages. "
        "Useful for getting detailed information from specific URLs. "
        "Input should be a valid URL."
    )
    
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_content_length: int = Field(default=50000, description="Maximum content length to return")
    
    def _run(self, url: str) -> str:
        """Scrape content from the given URL."""
        logger.info("Scraping web page", url=url)
        
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return f"Invalid URL: {url}"
            
            # Set up headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Make request
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract text content
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Limit content length
            if len(text_content) > self.max_content_length:
                text_content = text_content[:self.max_content_length] + "... [Content truncated]"
            
            logger.info("Web scraping completed", url=url, content_length=len(text_content))
            
            return f"Content from {url}:\n\n{text_content}"
            
        except Exception as e:
            logger.error("Web scraping failed", url=url, error=str(e))
            return f"Failed to scrape {url}: {str(e)}"


class URLValidatorTool(BaseTool):
    """Tool for validating and analyzing URLs."""
    
    name: str = "url_validator"
    description: str = (
        "Validate URLs and check their accessibility. "
        "Useful for verifying if links are working and getting basic information about web pages. "
        "Input should be a URL to validate."
    )
    
    timeout: int = Field(default=10, description="Request timeout in seconds")
    
    def _run(self, url: str) -> str:
        """Validate the given URL and return status information."""
        logger.info("Validating URL", url=url)
        
        try:
            # Basic URL validation
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                return f"Invalid URL: Missing protocol (http/https) in {url}"
            if not parsed_url.netloc:
                return f"Invalid URL: Missing domain in {url}"
            
            # Check URL accessibility
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; URLValidator/1.0)',
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.head(url, headers=headers, follow_redirects=True)
                
                result = {
                    "url": url,
                    "status_code": response.status_code,
                    "status": "accessible" if response.status_code == 200 else "error",
                    "content_type": response.headers.get('content-type', 'unknown'),
                    "content_length": response.headers.get('content-length', 'unknown'),
                    "final_url": str(response.url) if response.url != url else url,
                }
                
                # Format result
                formatted_result = f"URL Validation Results for {url}:\n"
                formatted_result += f"- Status: {result['status']}\n"
                formatted_result += f"- Status Code: {result['status_code']}\n"
                formatted_result += f"- Content Type: {result['content_type']}\n"
                formatted_result += f"- Content Length: {result['content_length']}\n"
                
                if result['final_url'] != url:
                    formatted_result += f"- Final URL (after redirects): {result['final_url']}\n"
                
                return formatted_result
                
        except httpx.TimeoutException:
            return f"URL validation failed: Timeout reached for {url}"
        except httpx.RequestError as e:
            return f"URL validation failed: Request error for {url} - {str(e)}"
        except Exception as e:
            logger.error("URL validation failed", url=url, error=str(e))
            return f"URL validation failed: {str(e)}"


class WebMonitoringTool(BaseTool):
    """Tool for monitoring web pages for changes."""
    
    name: str = "web_monitoring"
    description: str = (
        "Monitor web pages for changes by comparing current content with previous versions. "
        "Useful for tracking updates on websites. "
        "Input should be a URL to monitor."
    )
    
    def _run(self, url: str, previous_content: Optional[str] = None) -> str:
        """Monitor a web page for changes."""
        logger.info("Monitoring web page", url=url)
        
        try:
            # Get current content
            scraping_tool = WebScrapingTool()
            current_content = scraping_tool._run(url)
            
            if previous_content is None:
                return f"Baseline content captured for {url}. Use this content for future comparisons.\n\n{current_content[:500]}..."
            
            # Simple content comparison
            if current_content == previous_content:
                return f"No changes detected on {url}"
            else:
                # Calculate similarity (simple approach)
                similarity = self._calculate_similarity(current_content, previous_content)
                
                result = f"Changes detected on {url}!\n"
                result += f"Content similarity: {similarity:.1%}\n"
                result += f"Current content length: {len(current_content)} characters\n"
                result += f"Previous content length: {len(previous_content)} characters\n\n"
                result += f"Current content preview:\n{current_content[:500]}..."
                
                return result
                
        except Exception as e:
            logger.error("Web monitoring failed", url=url, error=str(e))
            return f"Web monitoring failed for {url}: {str(e)}"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


# Tool registry for easy access
WEB_TOOLS = {
    "search": WebSearchTool,
    "scraping": WebScrapingTool,
    "validator": URLValidatorTool,
    "monitoring": WebMonitoringTool,
}


def get_web_tool(tool_name: str, **kwargs) -> BaseTool:
    """Get a web tool by name with optional configuration."""
    if tool_name not in WEB_TOOLS:
        raise ValueError(f"Unknown web tool: {tool_name}. Available tools: {list(WEB_TOOLS.keys())}")
    
    tool_class = WEB_TOOLS[tool_name]
    return tool_class(**kwargs)


def get_all_web_tools(**kwargs) -> List[BaseTool]:
    """Get all available web tools."""
    return [tool_class(**kwargs) for tool_class in WEB_TOOLS.values()]
