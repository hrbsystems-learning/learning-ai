# run_flow.py
import asyncio
from prefect import flow, task
from prefect.concurrency.sync import run_sync_in_worker_thread

# Import the fully assembled crew from agents.py
from agents import investment_crew

@task(name="Run Investment Analysis Crew", retries=1, retry_delay_seconds=10)
def run_investment_crew_task(crew_inputs: dict) -> str:
    """
    A Prefect task that wraps the synchronous CrewAI process.
    It takes a dictionary of inputs and kicks off the crew's work.
    """
    print(f"--- TASK: Kicking off investment crew for sector: {crew_inputs.get('sector')} ---")
    
    # The kickoff method runs the entire sequence of tasks defined in the crew
    result = investment_crew.kickoff(inputs=crew_inputs)
    return result

@flow(name="AI Investment Analysis Workflow")
async def investment_analysis_flow(sector: str = "AI Chip Manufacturing"):
    """
    The main async Prefect flow that orchestrates our AI investment analysis.
    """
    print(f"--- FLOW: Starting AI Investment Analysis for sector: {sector} ---")
    
    inputs_for_crew = {'sector': sector}
    
    final_report = await run_sync_in_worker_thread(run_investment_crew_task, inputs_for_crew)
    
    print("\n" + "="*50)
    print("--- FLOW COMPLETE: FINAL INVESTMENT REPORT ---")
    print("="*50 + "\n")
    print(final_report)

if __name__ == "__main__":
    # This allows running the flow directly for testing
    asyncio.run(investment_analysis_flow(sector="Quantum Computing"))
    