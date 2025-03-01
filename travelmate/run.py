from dotenv import load_dotenv
import logging
from typing import Dict
from naptha_sdk.schemas import AgentRunInput
from travelmate.schemas import InputSchema, TripPlannerInput
from naptha_sdk.user import sign_consumer_id, get_private_key_from_pem
from crewai import Crew, Agent, Task, LLM
from crewai_tools import FirecrawlSearchTool
from textwrap import dedent
import os
from dev.agents import TravelAdvisors
from dev.tasks import TripTasks
import os
from pathlib import Path
from naptha_sdk import configs 
from naptha_sdk.client.naptha import Naptha
from naptha_sdk.configs import setup_module_deployment

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
class TripPlannerModule:
    def __init__(self, module_run):
        self.module_run = module_run
        self.llm = LLM(
            model="gpt-4o-mini",
            temperature=0.8,
        )
        
    def plan_trip(self, input_data: TripPlannerInput):
        try:
            logger.debug("Initializing trip planning...")
            
            agents = TravelAdvisors()
            tasks = TripTasks()
            destination_curator = agents.destination_curator()
            city_insider = agents.city_insider()
            travel_concierge_extraordinaire = agents.travel_concierge_extraordinaire()
            identify_task = tasks.identify_task(
                destination_curator,
                input_data.origin,
                input_data.cities,
                input_data.interests,
                input_data.date_range
            )
            gather_task = tasks.gather_task(
                city_insider,
                input_data.origin,
                input_data.interests,
                input_data.date_range
            )
            plan_task = tasks.plan_task(
                travel_concierge_extraordinaire,
                input_data.origin,
                input_data.interests,
                input_data.date_range
            )
            
            crew = Crew(
                agents=[destination_curator, city_insider, travel_concierge_extraordinaire],
                tasks=[identify_task, gather_task, plan_task],
                verbose=True
            )
            
            result = crew.kickoff()
            return result
            
        except Exception as e:
            logger.error(f"Error in trip planning: {e}")
            raise

original_load_llm_configs = configs.load_llm_configs

def patched_load_llm_configs(config_path):
    actual_path = str(Path(__file__).parent / "configs" / "llm_configs.json")
    return original_load_llm_configs(actual_path)

configs.load_llm_configs = patched_load_llm_configs

def run(module_run: Dict):
    """Entry point for the module"""
    if "agent_run_input" not in module_run:
        module_run["agent_run_input"] = module_run.get("inputs", {})
        del module_run["inputs"] 

    
    module_run = AgentRunInput(**module_run)
    module_run.agent_run_input = InputSchema(**module_run.agent_run_input)
    
    if isinstance(module_run.agent_run_input.tool_input_data, dict):
        module_run.agent_run_input.tool_input_data = TripPlannerInput(
            **module_run.agent_run_input.tool_input_data
        )
    
    planner = TripPlannerModule(module_run)
    method = getattr(planner, module_run.agent_run_input.tool_name)
    return method(module_run.agent_run_input.tool_input_data)

if __name__ == "__main__":
    import asyncio
    from naptha_sdk.client.naptha import Naptha
    from naptha_sdk.configs import setup_module_deployment
    
    naptha = Naptha()
    deployment = asyncio.run(
        setup_module_deployment(
            "agent",
            str(Path(__file__).parent / "configs" / "deployment.json"),
            node_url=os.getenv("NODE_URL")
        )
    )
    input_params = {
        "tool_name": "plan_trip",
        "tool_input_data": {
            "origin": "New York",
            "cities": "Paris, London, Rome",
            "date_range": "June 2024",
            "interests": "art, history, food"
        }
    }
    
    module_run = {
        "inputs": input_params,  
        "deployment": deployment,
        "consumer_id": naptha.user.id,
        "signature": sign_consumer_id(naptha.user.id, os.getenv("PRIVATE_KEY"))
    }
    
    response = run(module_run)
    print("Voyage Plan:", response)