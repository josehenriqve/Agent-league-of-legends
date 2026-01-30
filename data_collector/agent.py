
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
from data_collector.csv_tools import save_to_csv

def save_player_data(data_json: str) -> str:
    """
    Saves extracted player data to the standardized CSV.
    
    Args:
        data_json: A JSON string representing a list of player stats dictionaries.
                   The JSON MUST be a list of objects.
                   Each object should try to match the following keys as much as possible:
                   "OverviewPage", "Link", "Champion", "Kills", "Deaths", "Assists", "SummonerSpells", 
                   "Gold", "CS", "DamageToChampions", "VisionScore", "Items", "RoleBoundItem", 
                   "Trinket", "KeystoneMastery", "KeystoneRune", "PrimaryTree", "SecondaryTree", 
                   "Runes", "TeamKills", "TeamGold", "Team", "TeamVs", "PlayerWin", "DateTime_UTC", 
                   "DST", "Tournament", "Role", "Role_Number", "IngameRole", "Side", "UniqueLine", 
                   "UniqueLineVs", "UniqueRole", "UniqueRoleVs", "GameId", "MatchId", "GameTeamId", 
                   "GameRoleId", "GameRoleIdVs", "StatsPage"
    """
    try:
        # Clean up potential markdown formatting in the input
        cleaned_json = data_json.strip()
        if "```json" in cleaned_json:
            cleaned_json = cleaned_json.split("```json")[1].split("```")[0]
        elif "```" in cleaned_json:
            cleaned_json = cleaned_json.split("```")[1].split("```")[0]
            
        data = json.loads(cleaned_json)
        
        if isinstance(data, dict): # Handle single object case
            data = [data]
            
        result = save_to_csv(data)
        return result
    except json.JSONDecodeError:
        return "Error: Input was not valid JSON."
    except Exception as e:
        return f"Error saving data: {str(e)}"

# Create Agent 2 (Root Agent)
root_agent = Agent(
    model="gemini-2.5-flash",
    name="data_collector", # Name in the UI
    instruction="""
    You are a Data Collector Agent (Agent 2). 
    Your ONE AND ONLY goal is to build a dataset of League of Legends player statistics.
    
    You have a specialized sub-agent named 'lol_helper_agent' (Agent 1).
    
    WORKFLOW:
    1. When the user asks for data (e.g., "Busque as informações sobre o TitaN"), DELEGATE the request to 'lol_helper_agent'.
    2. Instruct 'lol_helper_agent' to find the data using its tools (MCP/Search).
    3. IMPORTANT: Tell 'lol_helper_agent' that it MUST return the found data to YOU (the parent agent) in a structured JSON format.
    4. Once you receive the data from 'lol_helper_agent', you MUST use the `save_player_data` tool to save it to the CSV.
    5. Confirm to the user that the data has been saved.
    
    DO NOT just display the data to the user. You MUST save it using `save_player_data`.
    """,
    tools=[save_player_data],
    sub_agents=[agent1]
)
