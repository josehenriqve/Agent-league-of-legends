import asyncio
from .client import LolFandomClient
from .simple_mcp import SimpleMCP
import json

# Initialize SimpleMCP server
mcp = SimpleMCP("LOL Fandom MCP", version="1.0.0")

# Initialize Client
client = LolFandomClient()

async def search_wiki(query: str, limit: int = 10) -> str:
    """
    Search for pages on the League of Legends Fandom Wiki.
    """
    try:
        results = await client.search_pages(query, int(limit))
        if not results:
            return f"No results found for '{query}'."
        
        formatted_results = [f"- {r['title']} (ID: {r['pageid']})" for r in results]
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error searching wiki: {e}"

async def read_page(title: str) -> str:
    """
    Get the content of a specific page from the LOL Fandom Wiki.
    """
    try:
        content = await client.get_page_content(title)
        return content
    except Exception as e:
        return f"Error reading page: {e}"

async def get_wiki_page_resource(title: str) -> str:
    """
    Access a wiki page as a resource.
    """
    try:
        return await client.get_page_content(title)
    except Exception as e:
        return f"Error reading resource: {e}"

async def get_player_stats(player_name: str, start_date: str = "2025-01-01 00:00:00", end_date: str = "2027-01-01 00:00:00") -> str:
    """
    Get player stats from the ScoreboardPlayers table via Cargo Query.
    """
    # Fields requested by the user, EXACTLY as provided
    fields = (
        "OverviewPage,Link,Champion,Kills,Deaths,Assists,SummonerSpells,Gold,CS,"
        "DamageToChampions,VisionScore,Items,RoleBoundItem,Trinket,KeystoneMastery,"
        "KeystoneRune,PrimaryTree,SecondaryTree,Runes,TeamKills,TeamGold,Team,TeamVs,"
        "PlayerWin,DateTime_UTC,DST,Tournament,Role,Role_Number,IngameRole,Side,"
        "UniqueLine,UniqueLineVs,UniqueRole,UniqueRoleVs,GameId,MatchId,GameTeamId,"
        "GameRoleId,GameRoleIdVs,StatsPage"
    )
    
    # Construct the 'where' clause securely but matching the user's exact format
    # User's URL: Link%3D%22TitaN%22AND DateTime_UTC...
    # Decoded: Link="TitaN"AND DateTime_UTC...
    # Note strictly NO SPACE before the first AND, and NO SPACE before the second AND based on the pattern
    # Wait, looking closely at the provided URL:
    # ...Link%3D%22TitaN%22AND DateTime_UTC... -> "AND 
    # ...%222025-01-01%2000:00:00%22AND DateTime_UTC... -> "AND
    # So the pattern is quote then AND immediately.
    
    where = f'Link="{player_name}"AND DateTime_UTC >= "{start_date}"AND DateTime_UTC < "{end_date}"'
    
    try:
        # We need to ensure client uses these parameters exactly.
        # limit isn't in the user's url example (implicit default) but I'll keep it as param or remove if needed.
        # User URL didn't have limit=50 explicit.
        # But for safety we usually add it. The user said "EXACTLY matches the example".
        # The example has `&format=json` at the end.
        # It does NOT have `&limit=...`.
        # However, `cargoquery` usually defaults to 50.
        # I will start by passing strict parameters.
        
        results = await client.cargo_query(
            tables="ScoreboardPlayers",
            fields=fields,
            where=where,
            limit=None # Allow client to handle default or omission
        )
        
        if not results:
            return f"No stats found for player '{player_name}' between {start_date} and {end_date}."
            
        # Format results as a JSON string for easy parsing by the LLM
        return json.dumps(results, indent=2)
            
    except Exception as e:
        return f"Error fetching player stats: {e}"

# Register tools
mcp.add_tool(
    search_wiki, 
    "search_wiki", 
    "Search for pages on the League of Legends Fandom Wiki.",
    {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search term"},
            "limit": {"type": "integer", "description": "Number of results (default 10)"}
        },
        "required": ["query"]
    }
)

mcp.add_tool(
    read_page,
    "read_page",
    "Get the content of a specific page from the LOL Fandom Wiki.",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "The exact title of the page"}
        },
        "required": ["title"]
    }
)

mcp.add_tool(
    get_player_stats,
    "get_player_stats",
    "Get detailed player stats from the ScoreboardPlayers table for a specific period.",
    {
        "type": "object",
        "properties": {
            "player_name": {"type": "string", "description": "The player's name (e.g., 'TitaN')"},
            "start_date": {"type": "string", "description": "Start date (blocks) (default '2025-01-01 00:00:00')"},
            "end_date": {"type": "string", "description": "End date (blocks) (default '2027-01-01 00:00:00')"}
        },
        "required": ["player_name"]
    }
)

# Register resource
mcp.add_resource(
    get_wiki_page_resource,
    "lol-fandom://{title}",
    "Wiki Page",
    "Access a wiki page content directly",
    "text/plain"
)

if __name__ == "__main__":
    try:
        asyncio.run(mcp.run())
    except KeyboardInterrupt:
        pass
    finally:
        # We can't really close the async client cleanly here easily without an event loop,
        # but in a subprocess it doesn't matter much.
        pass
