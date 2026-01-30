
from datetime import datetime
import sys
import os

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

# Updating import based on package rename
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# --- Tools ---

def search_tool(query: str) -> str:
    """
    Performs a web search using DuckDuckGo. 
    Use this ONLY to verify the correct spelling of a player's nickname.
    
    Args:
        query: The search query string (e.g., "League of Legends player [name]").
    """
    try:
        results = DDGS().text(query, max_results=2) # Reduced results as we just need the name
        if not results:
            return "No results found."
        
        summary = ""
        for result in results:
            summary += f"- {result['title']}: {result['body']}\n"
        return summary
    except Exception as e:
        return f"Error performing search: {str(e)}"

# --- MCP Setup ---

# Path to the lol-client-mcp directory relative to the project root
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lol_mcp_script = os.path.join(base_dir, "lol_fandom_mcp", "server.py")

# Ensure the script exists
if not os.path.exists(lol_mcp_script):
    print(f"WARNING: LOL Client MCP script not found at {lol_mcp_script}")

lol_client_toolset = McpToolset(
    connection_params=StdioServerParameters(
        command=sys.executable,
        args=[lol_mcp_script],
    )
)

# --- Agent ---

root_agent = Agent(
    model="gemini-2.5-flash",
    name="lol_helper_agent",
    instruction="""
    You are the 'League of Legends Helper' (Agent 1).
    Your ONLY purpose is to accurately retrieve player statistics for the Data Collector.
    
    STRICT WORKFLOW:
    1. **Identify Nickname**: The user will ask about a player (e.g., "titaN"). Use the `search_tool` to confirm the player's correct nickname and casing (e.g. search for "League of Legends player titaN").
    2. **Fetch Stats**: Once you have the confirmed nickname, use the `lol_client_toolset` (specifically `get_player_stats`) to get their stats.
       - Use the 'start_date' and 'end_date' provided by the user if available.
       - If no date is provided, use the tool's defaults.
    
    Do NOT answer general questions. Focus purely on this retrieval pipeline.
    Output the data clearly so the calling agent can parse it.
    """,
    tools=[search_tool, lol_client_toolset],
)
