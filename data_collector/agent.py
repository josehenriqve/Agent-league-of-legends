
import os
import sys
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure project root is in path to import software_bug_assistant
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from google.adk import Agent
from software_bug_assistant.agent import root_agent as agent1
from data_collector.csv_tools import save_player_data

# Create Agent 2 (Root Agent)
root_agent = Agent(
    model="gemini-2.5-flash",
    name="data_collector", # Name in the UI
    instruction="""
    You are a Data Collector Agent (Agent 2). 
    Your ONE AND ONLY goal is to build a dataset of League of Legends player statistics.
    
    You have a specialized sub-agent named 'lol_helper_agent' (Agent 1).
    
    WORKFLOW:
    1. When the user asks for data, DELEGATE to 'lol_helper_agent' to find it.
    2. 'lol_helper_agent' will return a JSON string.
    3. YOU MUST PASS THAT JSON STRING **EXACTLY** TO `save_player_data`.
    
    **EXAMPLES:**
    
    User: "Busque stats do TitaN"
    lol_helper_agent: [{"name": "TitaN", "kills": 10}]
    YOU (Action): Call `save_player_data({"data": [{"name": "TitaN", "kills": 10}]})`
    YOU (Output): "Dados salvos em csvs/informacoes.csv"
    
    User: "Info do Faker"
    lol_helper_agent: {"get_player_stats_response": ...}
    YOU (Action): Call `save_player_data({"data": {"get_player_stats_response": ...}})`
    YOU (Output): "Dados salvos."
    
    **STRICT RULES**:
    - **NEVER** print the JSON content in the chat.
    - **NEVER** summarize the stats.
    - **ALWAYS** call `save_player_data` immediately after receiving data.
    """,
    tools=[save_player_data],
    sub_agents=[agent1]
)

