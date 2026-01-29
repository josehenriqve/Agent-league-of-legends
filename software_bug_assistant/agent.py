
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



# --- LOL Fandom MCP Setup ---
lol_mcp_params = StdioServerParameters(
    command=sys.executable,
    args=["-m", "lol_fandom_mcp.server"],
    env=None
)
lol_mcp_toolset = McpToolset(connection_params=lol_mcp_params)

# --- Agent ---

root_agent = Agent(
    model="gemini-2.5-flash",
    name="lol_helper_agent",
    instruction="""
    You are a helpful assistant for League of Legends players.
    You have access to the League of Legends Fandom Wiki via the 'lol_fandom_mcp' tools.
    Use these tools to search for champions, items, lore, and other game information directly from the wiki.
    
    You also have access to real-time game data via the 'lol-clie
    """,
    tools=[lol_mcp_toolset],
)
