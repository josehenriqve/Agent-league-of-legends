
from datetime import datetime
from google.adk import Agent
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

# --- Agent ---

root_agent = Agent(
    model="gemini-2.5-flash",
    name="my_helper_agent",
    instruction="""
    You are a helpful assistant.
    Use the 'search_tool' to look up information on the internet.
    Use the 'get_current_date' tool if you need to know today's date.
    Answer concisely.
    """,
    tools=[get_current_date, search_tool],
)
