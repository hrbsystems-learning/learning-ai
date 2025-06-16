# agents.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Import our custom tools
from tools import search_tool, analyze_financial_data

load_dotenv()

# Initialize the LLM to be used by the crew
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

# --- AGENT DEFINITIONS ---

# 1. The Market Researcher Agent
market_researcher = Agent(
    role='Expert Market Researcher',
    goal='Identify the top 3-5 most promising companies in the {sector} sector.',
    backstory=(
        "You are a savvy researcher with a keen eye for emerging trends and key market players. "
        "Your analysis is data-driven and concise."
    ),
    tools=[search_tool],
    verbose=True
)

# 2. The Financial Analyst Agent
financial_analyst = Agent(
    role='Senior Financial Analyst',
    goal='Create a detailed financial report for each company provided.',
    backstory=(
        "You are a meticulous analyst who deciphers financial statements and market data "
        "to paint a clear picture of a company's health and potential."
    ),
    tools=[search_tool, analyze_financial_data],
    verbose=True
)

# 3. The Investment Advisor Agent
investment_advisor = Agent(
    role='Chief Investment Advisor',
    goal=(
        'Synthesize all research and analysis into a final, comprehensive investment report. '
        'Provide a ranked list of the analyzed companies and a final recommendation for the sector.'
    ),
    backstory=(
        "You are a seasoned investment strategist who translates complex data into actionable advice. "
        "Your final report is the ultimate guide for making investment decisions."
    ),
    verbose=True
)

# --- TASK DEFINITIONS ---

# Task for the researcher: Identify companies
research_task = Task(
    description='Search the web to identify the top 3-5 leading companies in the {sector} sector. Output a list of company names.',
    expected_output='A bulleted list of 3 to 5 company names. For example: - NVIDIA\n- AMD\n- Intel',
    agent=market_researcher
)

# Task for the analyst: Analyze each company
# The `context` parameter here is key. It receives the output from `research_task`.
analysis_task = Task(
    description=(
        'For each company in the provided list, perform a detailed financial analysis. '
        'Use the Financial Data Analysis Tool to get a summary and supplement it with web research.'
    ),
    expected_output=(
        'A detailed report for each company, including the financial summary and recent news or market sentiment.'
    ),
    agent=financial_analyst,
    context=[research_task]
)

# Task for the advisor: Compile the final report
# This task uses the context from the `analysis_task`.
recommendation_task = Task(
    description=(
        'Review the individual company analysis reports. Create a final, consolidated report that includes: '
        '1. An executive summary. '
        '2. A ranked list of the companies from most to least promising. '
        '3. A concluding investment thesis for the {sector} sector.'
    ),
    expected_output='A complete, well-formatted investment report ready for presentation.',
    agent=investment_advisor,
    context=[analysis_task]
)

# --- CREW DEFINITION ---

# Create the Crew object
investment_crew = Crew(
    agents=[market_researcher, financial_analyst, investment_advisor],
    tasks=[research_task, analysis_task, recommendation_task],
    llm=llm,
    verbose=2
)
