import requests
from typing import Dict, List
import json
import os

OPENDOTA_API_URL = "https://api.opendota.com/api"

def get_real_time_meta() -> Dict:
    """
    Fetches current hero statistics from OpenDota and identifies meta trends.
    This serves as a dynamic alternative when D2PT scraping is restricted.
    """
    try:
        # 1. Fetch hero stats (includes winrates by rank tier)
        print("[META] Fetching hero stats from OpenDota...")
        resp = requests.get(f"{OPENDOTA_API_URL}/heroStats", timeout=3)
        if resp.status_code != 200:
            return {"error": f"API error: {resp.status_code}"}
        
        heroes = resp.json()
        
        # 2. Filter for "Immortal" tier meta (tier 7/8 in OpenDota)
        # 8_win / 8_pick = Immortal Winrate
        meta_data = {
            "top_winrate": [],
            "most_picked": [],
            "tier_list": {
                "S": [],
                "A": [],
                "B": []
            }
        }
        
        # Calculate stats for each hero
        for h in heroes:
            picks = h.get("8_pick", 0)
            wins = h.get("8_win", 0)
            winrate = (wins / picks * 100) if picks > 50 else 0 # Threshold to avoid noise
            
            hero_info = {
                "id": h["id"],
                "name": h["localized_name"],
                "winrate": round(winrate, 2),
                "picks": picks,
                "roles": h.get("roles", [])
            }
            
            if picks > 100:
                if winrate >= 54:
                    meta_data["tier_list"]["S"].append(hero_info)
                elif winrate >= 51:
                    meta_data["tier_list"]["A"].append(hero_info)
                else:
                    meta_data["tier_list"]["B"].append(hero_info)
        
        # Sort by winrate
        meta_data["top_winrate"] = sorted(
            [h for h in heroes if h.get("8_pick", 0) > 100], 
            key=lambda x: (x.get("8_win", 0) / x.get("8_pick", 1)), 
            reverse=True
        )[:10]
        
        # Map to roles (Carry, Mid, etc.)
        meta_data["by_role"] = {
            "Carry": [],
            "Mid": [],
            "Offlane": [],
            "Support": []
        }
        
        for h in heroes:
            picks = h.get("8_pick", 0)
            if picks < 100: continue
            
            wr = (h.get("8_win", 0) / picks * 100)
            h_entry = {"name": h["localized_name"], "wr": round(wr, 2), "picks": picks}
            
            if "Carry" in h["roles"]:
                meta_data["by_role"]["Carry"].append(h_entry)
            if "Mid" in h["roles"]:
                meta_data["by_role"]["Mid"].append(h_entry)
            if "Offlane" in h["roles"]:
                meta_data["by_role"]["Offlane"].append(h_entry)
            if "Support" in h["roles"]:
                meta_data["by_role"]["Support"].append(h_entry)

        # Sort each role by winrate
        for role in meta_data["by_role"]:
            meta_data["by_role"][role] = sorted(meta_data["by_role"][role], key=lambda x: x["wr"], reverse=True)[:5]

        return meta_data

    except Exception as e:
        print(f"[META] Error fetching meta: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    meta = get_real_time_meta()
    if "error" not in meta:
        print(f"Top Carry: {meta['by_role']['Carry'][0]['name']} ({meta['by_role']['Carry'][0]['wr']}%)")
    else:
        print(meta["error"])
