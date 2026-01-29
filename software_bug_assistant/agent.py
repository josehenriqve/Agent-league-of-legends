
from datetime import datetime
import sys
import os

from google.adk import Agent
# Correct import path for MCP Toolset in ADK 1.22.0
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

# Updating import based on package rename
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# --- Tools ---

def get_current_date() -> dict:
    """
    Get the current date in the format YYYY-MM-DD
    """
    return {"current_date": datetime.now().strftime("%Y-%m-%d")}

def search_tool(query: str) -> str:
    """
    Performs a web search using DuckDuckGo.
    
    Args:
        query: The search query string.
    """
    try:
        results = DDGS().text(query, max_results=3)
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
# We assume the agent is run from the project root or we find the path dynamically
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lol_mcp_script = os.path.join(base_dir, "lol-client-mcp", "main.py")

# Using StdioServerParameters as required by the new McpToolset signature
lol_mcp_toolset = McpToolset(
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
    You are a helpful assistant for League of Legends players.
    You have access to real-time game data via the 'lol-client-mcp' tools.
    Use these tools to answer questions about the current game, player stats, items, etc.
    If the tool returns a connection error, inform the user that the game client might not be running or the game hasn't started.
    
    You also have general search capabilities and a date tool.
    """,
    tools=[get_current_date, search_tool, lol_mcp_toolset],
)
