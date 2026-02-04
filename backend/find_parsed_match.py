import requests

# Find a recent match from a pro or highly active account (e.g., account 70388657 is Dendi)
account_id = "70388657"
url = f"https://api.opendota.com/api/players/{account_id}/matches?limit=1"
response = requests.get(url)
matches = response.json()

if matches:
    match_id = matches[0]['match_id']
    print(f"Found match: {match_id}")
    
    detail_url = f"https://api.opendota.com/api/matches/{match_id}"
    res = requests.get(detail_url)
    data = res.json()
    
    print("\nRoot Keys:", sorted(data.keys()))
    print(f"\nVersion: {data.get('version')}")
    
    player = data.get("players", [{}])[0]
    print("\nPlayer 0 Stats:")
    target_stats = ["hero_damage", "tower_damage", "hero_healing", "total_gold", "kda", "kills", "deaths", "assists", "level"]
    for ts in target_stats:
        print(f"  {ts}: {player.get(ts)}")
else:
    print("Could not find a match.")
