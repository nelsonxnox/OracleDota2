import sys
import os
import json
import requests

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

match_id = "6775906014"

print(f"DEBUG: Inspecting Match {match_id}")
try:
    url = f"https://api.opendota.com/api/matches/{match_id}"
    response = requests.get(url, timeout=30)
    data = response.json()
    
    # 1. Check Root Keys
    print("\nRoot Keys:", sorted(data.keys()))
    
    # 2. Check "Parsed" Indicators
    indicators = ["version", "replay_salt", "chat", "objectives", "teamfights", "radiant_gold_adv"]
    print("\nParsed Indicators:")
    for ind in indicators:
        print(f"  {ind}: {'Present' if ind in data else 'Missing'} ({type(data.get(ind)).__name__})")
        if data.get(ind):
             print(f"    Value Sample: {str(data.get(ind))[:50]}")

    # 3. Check Player Stats for first player
    player = data.get("players", [{}])[0]
    print("\nPlayer 0 Stats:")
    target_stats = ["hero_damage", "tower_damage", "hero_healing", "total_gold", "kda", "kills", "deaths", "assists", "level"]
    for ts in target_stats:
        print(f"  {ts}: {player.get(ts)}")
        
    # 4. Check if damage is nested
    nested_damage = [k for k in player.keys() if "damage" in k.lower() and k not in target_stats]
    if nested_damage:
        print("\nOther damage fields:", nested_damage)
        
except Exception as e:
    print(f"Error: {e}")
