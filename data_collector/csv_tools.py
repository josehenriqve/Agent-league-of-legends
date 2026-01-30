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

DATA_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_output")
CSV_FILE_PATH = os.path.join(DATA_OUTPUT_DIR, "player_stats.csv")

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
