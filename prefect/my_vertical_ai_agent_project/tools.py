# tools.py
import pandas as pd
import numpy as np
from langchain.tools import tool
from crewai_tools import SerperDevTool

# Instantiate the search tool for web research
search_tool = SerperDevTool()

@tool("Financial Data Analysis Tool")
def analyze_financial_data(company_name: str) -> str:
    """
    Simulates fetching and analyzing key financial data for a given company.
    Use this tool to get a financial summary including revenue, profit, and key ratios.
    It returns a formatted string with the analysis.
    """
    print(f"--- TOOL: Analyzing financial data for {company_name}... ---")
    
    # In a real scenario, this would be an API call to a financial data provider.
    # Here, we simulate it with pandas and numpy for demonstration.
    data = {
        'Year': [2021, 2022, 2023],
        'Revenue (M)': np.random.uniform(5000, 20000, 3).tolist(),
        'Net Income (M)': np.random.uniform(500, 5000, 3).tolist(),
    }
    df = pd.DataFrame(data)

    # Perform some analysis
    df['Profit Margin (%)'] = (df['Net Income (M)'] / df['Revenue (M)']) * 100
    latest_revenue = df.iloc[-1]['Revenue (M)']
    avg_profit_margin = df['Profit Margin (%)'].mean()
    growth_rate = ((df.iloc[-1]['Revenue (M)'] / df.iloc[0]['Revenue (M)']) - 1) * 100

    # Format the output as a string for the LLM
    summary = (
        f"Financial Summary for {company_name}:\n"
        f"- Latest Annual Revenue: ${latest_revenue:,.2f} Million\n"
        f"- Average 3-Year Profit Margin: {avg_profit_margin:.2f}%\n"
        f"- 3-Year Revenue Growth Rate: {growth_rate:.2f}%\n"
        f"Overall Assessment: The company shows a growth rate of {growth_rate:.2f}% "
        f"with a solid average profit margin. Further investigation into market position is advised."
    )
    return summary
