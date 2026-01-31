
import os
import sys
import json

# Add project root
sys.path.append(os.getcwd())

from data_collector.agent import save_player_data
from data_collector.csv_tools import CSV_FILE_PATH, DATA_OUTPUT_DIR

print(f"Output Config:\nDir: {DATA_OUTPUT_DIR}\nFile: {CSV_FILE_PATH}")

# scenario 1: Nested structure (what Agent 1 likely returns)
nested_json = json.dumps({
    "player_name": "TitaN",
    "stats": [
        {
             "OverviewPage": "TestPage",
             "Link": "TitaN",
             "Champion": "Ezreal",
             "Kills": "10",
             "Deaths": "0",
             "Assists": "5"
        }
    ]
})

print("\n--- Testing Nested JSON ---")
result = save_player_data(nested_json)
print(f"Result: {result}")

if os.path.exists(CSV_FILE_PATH):
    print("File created. Content:")
    with open(CSV_FILE_PATH, 'r') as f:
        print(f.read())
else:
    print("File NOT created.")

# Clean up
if os.path.exists(CSV_FILE_PATH):
    os.remove(CSV_FILE_PATH)
    print("Cleaned up file.")
