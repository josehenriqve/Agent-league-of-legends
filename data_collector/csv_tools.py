import csv
import os
from typing import List, Dict, Any

# Define the standard columns strictly as requested
STANDARD_COLUMNS = [
    "OverviewPage", "Link", "Champion", "Kills", "Deaths", "Assists", "SummonerSpells", "Gold", "CS",
    "DamageToChampions", "VisionScore", "Items", "RoleBoundItem", "Trinket", "KeystoneMastery",
    "KeystoneRune", "PrimaryTree", "SecondaryTree", "Runes", "TeamKills", "TeamGold", "Team", "TeamVs",
    "PlayerWin", "DateTime_UTC", "DST", "Tournament", "Role", "Role_Number", "IngameRole", "Side",
    "UniqueLine", "UniqueLineVs", "UniqueRole", "UniqueRoleVs", "GameId", "MatchId", "GameTeamId",
    "GameRoleId", "GameRoleIdVs", "StatsPage"
]


DATA_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "csvs")
CSV_FILE_PATH = os.path.join(DATA_OUTPUT_DIR, "informacoes.csv")

def ensure_directory_exists():
    """Ensures the data output directory exists."""
    if not os.path.exists(DATA_OUTPUT_DIR):
        os.makedirs(DATA_OUTPUT_DIR)


def save_to_csv(player_stats_list: List[Dict[str, Any]]) -> str:
    """
    Saves a list of player stats to the CSV file.
    
    Args:
        player_stats_list: List of dictionaries containing player stats.
                          Each dictionary CAN contain extra keys (will be ignored)
                          or missing keys (will be filled with empty string).
    """
    ensure_directory_exists()
    
    file_exists = os.path.exists(CSV_FILE_PATH)
    
    try:
        with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=STANDARD_COLUMNS, extrasaction='ignore')
            
            if not file_exists:
                writer.writeheader()
            
            for stats in player_stats_list:
                # Ensure all columns exist, fill with empty string if missing
                row = {col: stats.get(col, "") for col in STANDARD_COLUMNS}
                writer.writerow(row)
                
        return f"Successfully saved {len(player_stats_list)} records to {CSV_FILE_PATH}"
    except Exception as e:
        return f"Error saving to CSV: {str(e)}"

def save_player_data(data: Any) -> str:
    """
    Wrapper function to be used by the Agent.
    Parses complex/nested JSON inputs and saves them using save_to_csv.
    """
    import json
    import sys
    
    print(f"[CSV Tool] Received data (type: {type(data)}): {str(data)[:200]}...", file=sys.stderr)

    try:
        parsed_data = []
        if isinstance(data, str):
            # Clean md blocks
            cleaned = data.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0]
            parsed_data = json.loads(cleaned)
        else:
            parsed_data = data

        # Deep extraction logic
        if isinstance(parsed_data, dict):
            # Check for MCP wrapper
            if "get_player_stats_response" in parsed_data:
                 print("[CSV Tool] Found 'get_player_stats_response' wrapper", file=sys.stderr)
                 content = parsed_data["get_player_stats_response"].get("content", [])
                 if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict) and "text" in content[0]:
                     inner_text = content[0]["text"]
                     print("[CSV Tool] Extracting inner text from content...", file=sys.stderr)
                     try:
                        parsed_data = json.loads(inner_text)
                     except json.JSONDecodeError:
                        pass
            
            # Check for 'title' wrapper (user's specific case: [{"title": {...}}])
            # Wait, user example was list of dicts with "title".
            # '[{"title": {"OverviewPage": ...'
            
            final_list = []
            if isinstance(parsed_data, dict):
                 if "stats" in parsed_data and isinstance(parsed_data["stats"], list):
                     final_list = parsed_data["stats"]
                 elif "results" in parsed_data and isinstance(parsed_data["results"], list):
                     final_list = parsed_data["results"]
                 else:
                     final_list = [parsed_data]
            elif isinstance(parsed_data, list):
                final_list = parsed_data
            else:
                 return "Error: Parsed data is not a list or dict."
        
        elif isinstance(parsed_data, list):
            final_list = parsed_data
        else:
            return "Error: Input data is not a list or dict."

        # Pre-processing to flatten "title" wrapper if present
        # User reported: [{"title": {"OverviewPage": ...}}]
        processed_list = []
        for item in final_list:
            if isinstance(item, dict) and "title" in item and isinstance(item["title"], dict):
                # Flatten: take the inner dict
                processed_list.append(item["title"])
            else:
                processed_list.append(item)

        print(f"[CSV Tool] Saving {len(processed_list)} items...", file=sys.stderr)
        return save_to_csv(processed_list)

    except Exception as e:
        print(f"[CSV Tool] Error: {str(e)}", file=sys.stderr)
        return f"Error processing data: {str(e)}"
