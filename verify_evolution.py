import sys
import os

# Adjust paths to import from backend
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from services.opendota_service import get_match_data, process_match_data, generate_ai_context
from services.ai_coach import oracle

def verify():
    # TI10 Grand Final Game 5: Spirit vs LGD (Definitely parsed)
    match_id = "6227463326" 
    print(f"Testing with Match ID: {match_id}")
    
    raw_data = get_match_data(match_id)
    if "error" in raw_data:
        print(f"Error fetching match: {raw_data['error']}")
        # Fallback to a mock if API fails
        print("Attempting to verify with a simple mock...")
        mock_verify()
        return

    processed = process_match_data(raw_data)
    print("\n[PROCESSED DATA KEYS]:", list(processed.keys()))
    
    # Check for new keys
    meta = processed["metadata"]
    print(f"Picks/Bans found: {len(meta.get('picks_bans', []))}")
    print(f"Objectives found: {len(meta.get('objectives', []))}")
    
    if processed["players"]:
        sample_player = processed["players"][0]
        print(f"\nSample Player: {sample_player['name']} ({sample_player['hero_name']})")
        print(f"Laning Efficiency: {sample_player.get('laning_efficiency')}%")
        print(f"Deaths Vision Log Size: {len(sample_player.get('deaths_with_vision', []))}")
    
    context = generate_ai_context(processed, deep_mode=True)
    
    print("\n--- AI CONTEXT PREVIEW (FIRST 1000 CHARS) ---")
    print(context[:1000])
    
    # Verify presence of key terms
    print("\n--- VERIFICATION CHECKLIST ---")
    checklist = {
        "DRAFT": "--- DRAFT" in context,
        "OBJETIVOS": "--- OBJETIVOS" in context,
        "Eficiencia": "Eficiencia" in context,
        "Muertes sin visión": "Muertes sin visión" in context
    }
    for key, found in checklist.items():
        print(f"Contains '{key}': {found}")

def mock_verify():
    # Simple manual check of data structures
    mock_processed = {
        "metadata": {
            "match_id": "12345",
            "winner": "Radiant",
            "duration_minutes": 40,
            "picks_bans": [{"hero_id": 1, "is_pick": True, "order": 1}],
            "objectives": [{"type": "CHAT_MESSAGE_ROSHAN_KILL", "time": 1200}]
        },
        "players": [
            {
                "name": "TestPlayer",
                "hero_name": "Anti-Mage",
                "pos_guess": 1,
                "team": "Radiant",
                "kda": "10/0/5",
                "networth": 20000,
                "hero_damage": 15000,
                "tower_damage": 5000,
                "hero_healing": 0,
                "final_items": ["Battle Fury"],
                "lh_at_10": 80,
                "dn_at_10": 10,
                "gold_at_10": 5000,
                "laning_efficiency": 97.5,
                "deaths_with_vision": [{"time": 15, "has_vision": False}],
                "stuns": 0,
                "buybacks": 0,
                "obs_placed": 0,
                "sen_placed": 0,
                "full_item_log": [],
                "ability_build": ["Blink"] * 10,
                "obs_details": [],
                "sen_details": []
            }
        ]
    }
    context = generate_ai_context(mock_processed, deep_mode=True)
    print("Mock Context Check (DRAFT):", "--- DRAFT" in context)
    print("Mock Context Check (Eficiencia):", "Eficiencia" in context)

if __name__ == "__main__":
    verify()
