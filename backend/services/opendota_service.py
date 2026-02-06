"""
OracleDota - Match Data Ingestion Module
Uses OpenDota API (more reliable than Stratz for programmatic access)
"""
import requests
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

OPENDOTA_API_URL = "https://api.opendota.com/api"

# Cache for hero, item and ability names
HERO_CACHE = {}
ITEM_CACHE = {}
ITEM_ID_TO_NAME = {}
ABILITY_CACHE = {}
ABILITY_ID_TO_NAME = {}

def get_hero_names():
    """Fetches hero list from OpenDota for mapping ID -> Name"""
    global HERO_CACHE
    if HERO_CACHE:
        return HERO_CACHE
    
    try:
        resp = requests.get(f"{OPENDOTA_API_URL}/heroes", timeout=10)
        if resp.status_code == 200:
            heroes = resp.json()
            # Clear cache to ensure new format is used
            HERO_CACHE.clear()
            for h in heroes:
                HERO_CACHE[int(h['id'])] = h
            return HERO_CACHE
    except Exception as e:
        print(f"[ERROR] Could not fetch hero names: {e}")
    return {}

def get_item_names():
    """Fetches item list from OpenDota constants and prepares ID mapping"""
    global ITEM_CACHE, ITEM_ID_TO_NAME
    if ITEM_CACHE:
        return ITEM_CACHE, ITEM_ID_TO_NAME
    try:
        resp = requests.get(f"{OPENDOTA_API_URL}/constants/items", timeout=10)
        if resp.status_code == 200:
            items = resp.json()
            ITEM_CACHE = {k: v.get('dname', k) for k, v in items.items()}
            ITEM_ID_TO_NAME = {v.get('id'): v.get('dname', k) for k, v in items.items() if 'id' in v}
            return ITEM_CACHE, ITEM_ID_TO_NAME
    except Exception as e:
        print(f"[ERROR] Could not fetch item names: {e}")
    return {}, {}

def get_ability_names():
    """Fetches ability list from OpenDota constants with ID mapping"""
    global ABILITY_CACHE, ABILITY_ID_TO_NAME
    if ABILITY_CACHE:
        return ABILITY_CACHE, ABILITY_ID_TO_NAME
    try:
        resp = requests.get(f"{OPENDOTA_API_URL}/constants/abilities", timeout=10)
        if resp.status_code == 200:
            abilities = resp.json()
            # Abilities in constants are keyed by string name
            ABILITY_CACHE = {k: v.get('dname', k) for k, v in abilities.items()}
            # Map integer ID to localized name
            ABILITY_ID_TO_NAME = {v.get('id'): v.get('dname', k) for k, v in abilities.items() if 'id' in v}
            return ABILITY_CACHE, ABILITY_ID_TO_NAME
    except Exception as e:
        print(f"[ERROR] Could not fetch ability names: {e}")
    return {}, {}

def get_match_data(match_id: str) -> Dict:
    """
    Fetches match data from OpenDota API.
    OpenDota is more bot-friendly than Stratz and doesn't have Cloudflare protection.
    """
    url = f"{OPENDOTA_API_URL}/matches/{match_id}"
    
    try:
        print(f"[FETCH] Fetching match {match_id} from OpenDota...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 404:
            return {"error": f"Match {match_id} not found. It may be private or too old."}
        
        if response.status_code != 200:
            return {"error": f"OpenDota API error: {response.status_code}"}
        
        data = response.json()
        
        # Validación de Parseo
        # Si no tiene 'version', es que no ha sido procesada profundamente (Replay parsed)
        # También verificamos si faltan campos clave de telemetría
        is_fully_parsed = data.get("version") is not None
        has_telemetry = data.get("radiant_gold_adv") is not None
        
        if not is_fully_parsed or not has_telemetry:
            print(f"[FETCH] Match {match_id} not fully parsed or missing telemetry. Requesting parse job...")
            # Solicitamos parseo para futuro, pero NO bloqueamos
            try:
                requests.post(f"{OPENDOTA_API_URL}/request/{match_id}", timeout=5)
            except:
                pass # Non-blocking
            
            # Marcamos que los datos son parciales
            data["partial_data"] = True
            
            # Si no hay ni siquiera datos básicos de jugadores, ahí sí es error
            if not data.get("players"):
                return {"error": "Match data unavailable. Please wait for OpenDota to process it."}
        
        return data

    except requests.exceptions.Timeout:
        return {"error": "Request timeout. OpenDota might be slow, try again."}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def process_match_data(match_data: Dict) -> Dict:
    """
    Extracts and structures key information from OpenDota match data.
    """
    if "error" in match_data:
        return match_data

    processed = {
        "metadata": {},
        "players": [],
        "teamfights": []
    }

    # 1. Metadata
    radiant_win = match_data.get("radiant_win")
    winner = "Radiant" if radiant_win else "Dire"
    duration_min = (match_data.get("duration") or 0) // 60
    match_id = match_data.get("match_id")
    
    processed["metadata"] = {
        "match_id": match_id,
        "winner": winner,
        "duration_minutes": duration_min,
        "patch": match_data.get("patch", "Unknown"),
        "game_mode": match_data.get("game_mode", 0),
        "radiant_score": match_data.get("radiant_score", 0),
        "dire_score": match_data.get("dire_score", 0),
        "gold_advantage": match_data.get("radiant_gold_adv", []),
        "xp_advantage": match_data.get("radiant_xp_adv", []),
        "partial_data": match_data.get("partial_data", False),
        "picks_bans": match_data.get("picks_bans", []),
        "objectives": match_data.get("objectives", [])
    }

    # 2. Player Performance
    players = match_data.get("players", [])
    
    # Sort players by team to help with role ranking
    radiant_p = [p for p in players if p.get("player_slot", 0) < 128]
    dire_p = [p for p in players if p.get("player_slot", 0) >= 128]
    
    # Helper to guess Pos (1-5) based on Networth rank within team
    def assign_pos(team_players):
        # Sort by total_gold descending
        sorted_p = sorted(team_players, key=lambda x: x.get("total_gold", 0), reverse=True)
        # We'll use a mix of lane_role and gold ranking
        for i, p in enumerate(sorted_p):
            p["networth_rank"] = i + 1 # 1 is richest
            
    assign_pos(radiant_p)
    assign_pos(dire_p)

    # Pre-fetch naming mappings
    hero_names = get_hero_names()
    item_names, item_ids = get_item_names()
    ability_names, ability_ids = get_ability_names()

    for p in players:
        player_slot = p.get("player_slot", 0)
        is_radiant = player_slot < 128
        team = "Radiant" if is_radiant else "Dire"
        
        # Determine likely Pos based on gold rank and lane
        nw_rank = p.get("networth_rank", 3)
        lane_role = p.get("lane_role", 0)
        
        # DEBUG: Ver qué datos llegan realmente
        print(f"Player: {p.get('personaname')} (Hero: {p.get('hero_id')}) -> LaneRole: {lane_role}, Lane: {p.get('lane')}, Roam: {p.get('is_roaming')}")

        # FALLBACK: Si lane_role es 0, intentar inferirlo de 'lane' (geográfico)
        if not lane_role or lane_role == 0:
            geo_lane = p.get("lane", 0) # 1=Bot, 2=Mid, 3=Top
            if geo_lane == 2:
                lane_role = 2 # Mid es Mid
            elif geo_lane == 1: # Bot Lane
                lane_role = 1 if is_radiant else 3 # Radiant Safe / Dire Off
            elif geo_lane == 3: # Top Lane
                lane_role = 3 if is_radiant else 1 # Radiant Off / Dire Safe
            elif p.get("is_roaming"):
                lane_role = 4 # Roaming/Jungle

        # Heuristic for Pos
        if lane_role == 2: # Mid is almost always Pos 2
            pos_guess = 2
        elif lane_role == 1: # Safe Lane
            pos_guess = 1 if nw_rank <= 2 else 5
        elif lane_role == 3: # Off Lane
            pos_guess = 3 if nw_rank <= 3 else 4
        else: # Roaming/Jungle/Unknown
            pos_guess = 4 if nw_rank >= 4 else 3

        # Refine Pos 1 vs 2 if both in same team
        # (This is basic but better than before)
        
        # Get player name with better fallback for Pros
        player_name = p.get("personaname") or p.get("name") or "Anonymous"
        
        # Hero name resolution
        hero_id = p.get("hero_id")
        hero_data = hero_names.get(hero_id)
        
        if isinstance(hero_data, dict):
            hero_name = hero_data.get("localized_name", f"Hero {hero_id}")
            hero_img_name = hero_data.get("name", "").replace("npc_dota_hero_", "")
        else:
            hero_name = str(hero_data) if hero_data else f"Hero {hero_id}"
            hero_img_name = "abaddon"
        
        stats = {
            "name": player_name,
            "hero_id": hero_id,
            "hero_name": hero_name,
            "player_slot": player_slot, # Needed for linking to teamfights
            "team": team,
            "kda": f"{p.get('kills', 0)}/{p.get('deaths', 0)}/{p.get('assists', 0)}",
            "networth": p.get("total_gold") or 0,
            "hero_damage": p.get("hero_damage") or 0,
            "tower_damage": p.get("tower_damage") or 0,
            "hero_healing": p.get("hero_healing") or 0,
            "lh_at_10": p.get("lh_t", [0])[min(10, len(p.get("lh_t", [0]))-1)] if p.get("lh_t") else 0,
            "dn_at_10": p.get("dn_t", [0])[min(10, len(p.get("dn_t", [0]))-1)] if p.get("dn_t") else 0,
            "gold_at_10": p.get("gold_t", [0])[min(10, len(p.get("gold_t", [0]))-1)] if p.get("gold_t") else 0,
            "level": p.get("level", 1),
            "stuns": round(p.get("stuns") or 0, 1),
            "buybacks": p.get("buybacks") or 0,
            "obs_placed": p.get("obs_placed") or 0,
            "sen_placed": p.get("sen_placed") or 0,
            "kill_streaks": p.get("kill_streaks", {}),
            "player_slot": player_slot, # Needed for linking to teamfights
            "lh_dn": f"{p.get('last_hits', 0)}/{p.get('denies', 0)}",
            "gpm_xpm": f"{p.get('gold_per_min', 0)}/{p.get('xp_per_min', 0)}",
            "lane_role": lane_role, # 1=Safe, 2=Mid, 3=Off, 4=Jungle
            "pos_guess": pos_guess,
            "nw_rank": nw_rank,
            "camps_stacked": p.get("camps_stacked", 0),
            "runes_collected": len(p.get("runes_log", [])),
            "xp_at_10": p.get("xp_t", [0]*11)[10] if p.get("xp_t") and len(p.get("xp_t")) > 10 else 0,
            "multi_kills": p.get("multi_kills", {}),
            "deaths_log": p.get("deaths_log", []),
        }
        
        # Laning Efficiency Calculation (Approx 82 creeps at 10 min)
        total_possible_lh = 82 if pos_guess != 2 else 100 # Mid usually has more
        stats["laning_efficiency"] = round((stats["lh_at_10"] / total_possible_lh) * 100, 1) if total_possible_lh > 0 else 0

        
        # Item timings from purchase_log (Full log)
        stats["full_item_log"] = []
        purchase_log = p.get("purchase_log", [])
        for purchase in purchase_log:
            item_key = purchase.get("key", "unknown_item")
            time_min = purchase.get("time", 0) // 60
            # Get clean name from constants if possible
            clean_name = item_names.get(item_key, item_key.replace("_", " ").title())
            
            if not item_key.startswith(("ward", "clarity", "tango", "flask", "smoke", "enchanted_mango")):
                stats["full_item_log"].append({
                    "item": clean_name,
                    "time": time_min
                })
        
        # Final Items (Inventory)
        stats["final_items"] = []
        for i in range(6):
            item_id = p.get(f"item_{i}")
            if item_id:
                stats["final_items"].append(item_ids.get(item_id, f"Unknown Item {item_id}"))
        
        # Neutral Item
        neutral_item_id = p.get("item_neutral")
        if neutral_item_id:
            stats["neutral_item"] = item_ids.get(neutral_item_id, f"Unknown Neutral {neutral_item_id}")
        else:
            stats["neutral_item"] = "None"
            
        # 3. Kill Log / Map Presence
        stats["kill_log"] = []
        for k in p.get("kills_log", []):
            stats["kill_log"].append({
                "time": k.get("time", 0) // 60,
                "victim": k.get("key", "unknown")
            })

        # Ability Build
        stats["ability_build"] = []
        for ab_id in p.get("ability_upgrades_arr", []):
            ab_name = ability_ids.get(ab_id, f"Unknown Ability {ab_id}")
            stats["ability_build"].append(ab_name)

        # Detailed Ward Logs (with coordinates)
        def process_ward_log(log_key):
            detailed_log = []
            placed = p.get(log_key, [])
            for ward in placed:
                detailed_log.append({
                    "time": ward.get("time", 0) // 60,
                    "x": ward.get("x", 0),
                    "y": ward.get("y", 0)
                })
            return detailed_log

        stats["obs_details"] = process_ward_log("obs_log")
        stats["sen_details"] = process_ward_log("sen_log")

        # 3.5 Death Vision Analysis
        # Check if teammate wards were active near death location
        stats["deaths_with_vision"] = []
        team_obs = []
        for other_p in players:
            if (other_p.get("player_slot", 0) < 128) == is_radiant:
                team_obs.extend(other_p.get("obs_log", []))
        
        for d in stats["deaths_log"]:
            d_time = d.get("time", 0)
            d_x = d.get("x", 0)
            d_y = d.get("y", 0)
            
            has_vision = False
            for ward in team_obs:
                w_time = ward.get("time", 0)
                # Observer ward duration is 6 mins (360s)
                if w_time <= d_time <= w_time + 360:
                    # Euclidean distance check (approx 1600 units is ward vision range)
                    # OpenDota coordinates are 64-192 or so, map is 128x128
                    dist = ((ward.get("x", 0) - d_x)**2 + (ward.get("y", 0) - d_y)**2)**0.5
                    if dist < 20: # Rough estimate for "near" in OpenDota units
                        has_vision = True
                        break
            
            stats["deaths_with_vision"].append({
                "time": d_time // 60,
                "has_vision": has_vision,
                "victim_x": d_x,
                "victim_y": d_y
            })
        
        # 4. Movement History (lane_pos)
        # OpenDota provides lane_pos as { "0": {x,y}, "1": {x,y}... }
        raw_lane_pos = p.get("lane_pos", {})
        stats["movement_history"] = {}
        if isinstance(raw_lane_pos, dict):
            for t_min, pos in raw_lane_pos.items():
                try:
                    # Convert coordinates to 0-100% scale (approximate)
                    # Dota map is 128x128 in OpenDota lane_pos usually
                    stats["movement_history"][int(t_min)] = {
                        "x": pos.get("x", 0),
                        "y": pos.get("y", 0)
                    }
                except:
                    pass
        
        processed["players"].append(stats)

    # 4. Teamfights Processing
    teamfights = match_data.get("teamfights", [])
    if teamfights:
        for i, tf in enumerate(teamfights):
            start = tf.get("start", 0) // 60
            end = tf.get("end", 0) // 60
            
            # Identify participants and key actions
            tf_data = {
                "id": i + 1,
                "start": start,
                "end": end,
                "deaths": tf.get("deaths", 0),
                "players_involved": []
            }
            
            for tf_player in tf.get("players", []):
                # We need to map player_slot back to our hero/player info
                # tf_player does not have hero_id, only ability/item uses and stats for that fight
                # We assume the order matches or use direct match if possible, but OpenDota tf players list is indexed by slot usually? 
                # Actually OpenDota teamfight players list usually has 10 entries corresponding to slots 0-4 and 128-132.
                # However, let's keep it simple: we can see ability uses.
                
                # Filter out players who didn't participate (no damage, no healing, no deaths, no kills)
                if (tf_player.get("damage") or 0) > 0 or (tf_player.get("healing") or 0) > 0 or (tf_player.get("deaths") or 0) > 0:
                    
                     # Convert ability/item keys to names
                    abilities_used = {}
                    for ab_k, ab_v in tf_player.get("ability_uses", {}).items():
                        ab_name = ability_names.get(ab_k, ab_k)
                        abilities_used[ab_name] = ab_v
                        
                    tf_data["players_involved"].append({
                        "damage": tf_player.get("damage", 0),
                        "healing": tf_player.get("healing", 0),
                        "killed": tf_player.get("killed", 0),
                        "deaths": tf_player.get("deaths", 0),
                        "abilities_used": abilities_used
                    })
            
            processed["teamfights"].append(tf_data)

    return processed

def summarize_items(item_log: List[Dict]) -> str:
    """Summarizes item timings into conclusions to save tokens."""
    try:
        if not item_log: return "Sin compras clave."
        
        # Identify key early/mid game items
        key_items = ["Blink Dagger", "Black King Bar", "Battle Fury", "Maelstrom", "Radiance", "Dagon", "Orchid Malevolence", "Manta Style"]
        summaries = []
        for entry in item_log:
            item = entry.get('item', 'Item Unknown')
            time = entry.get('time', 0)
            if item in key_items or (isinstance(time, int) and time > 30): # Key items or late game additions
                summaries.append(f"{item} ({time}m)")
        
        # If too many items, just show last 5 and key ones
        if len(summaries) > 8:
            return ", ".join(summaries[:3] + ["..."] + summaries[-3:])
        return ", ".join(summaries)
    except Exception as e:
        print(f"[RECOVERY] summarize_items failed: {e}")
        return "Resumen de items no disponible."

def generate_ai_context(data: Dict, deep_mode: bool = False) -> str:
    """
    Generates context in two layers:
    Base (Cheap): Basic stats, final build, team comp.
    Deep (Expensive): Full timelines, ward logs, ability builds, detailed teamfights.
    """
    if "error" in data:
        return "No hay datos de la partida disponibles."

    meta = data["metadata"]
    is_partial = meta.get("partial_data", False)
    hero_names = get_hero_names()
    
    radiant_heroes = [p["hero_name"] for p in data["players"] if p["team"] == "Radiant"]
    dire_heroes = [p["hero_name"] for p in data["players"] if p["team"] == "Dire"]

    context = []
    
    if is_partial:
        context.append("⚠️ NOTA PARA EL COACH: Los datos extendidos (daño, visión, posiciones) no están disponibles en la API de OpenDota para esta partida específica. ")
        context.append("Esto suele ocurrir en partidas muy antiguas (archivos expirados) o que aún no han sido procesadas. ")
        context.append("NO menciones que los jugadores hicieron 0 daño como un error de juego; simplemente explica que esos datos no están disponibles en este momento. Enfócate en KDA y Oro.\n")

    context.extend([
        f"PARTIDA #{meta['match_id']} | GANÓ: {meta['winner']} | DURACIÓN: {meta['duration_minutes']}m",
        f"EQUIPOS: Radiant ({', '.join(radiant_heroes)}) vs Dire ({', '.join(dire_heroes)})",
    ])

    if data.get("partial_data"):
        context.insert(0, "⚠️ ADVERTENCIA: PARTIDA NO PARSEADA COMPLETAMENTE (Datos de wards/vision limitados)")

    if deep_mode:
        gold_adv = meta.get("gold_advantage", [])
        if gold_adv:
            peak = max(gold_adv) if max(gold_adv) > abs(min(gold_adv)) else min(gold_adv)
            context.append(f"ECONOMÍA: Ventaja Oro Pico: {peak} para {'Radiant' if peak > 0 else 'Dire'}")

    context.append("\n--- JUGADORES ---")
    
    for p in data["players"]:
        # Basic Stats (Always included)
        p_row = (f"{p['name']} ({p['hero_name']}): Pos {p['pos_guess']} | KDA: {p['kda']} | "
                 f"NW: {p['networth']} | Daño Héroes: {p['hero_damage']} | "
                 f"Daño Torres: {p['tower_damage']} | Curación: {p['hero_healing']} | "
                 f"Build: {', '.join(p['final_items'])}")
        context.append(p_row)

        if deep_mode:
            # Detailed Stats for deep analysis
            timing_summary = summarize_items(p['full_item_log'])
            
            # Ward Logs Formatting
            obs_log_str = ", ".join([f"Min {w['time']}(x:{w['x']},y:{w['y']})" for w in p.get('obs_details', [])])
            if not obs_log_str: obs_log_str = "Ninguno (o datos de log no disponibles)"
            
            sen_log_str = ", ".join([f"Min {w['time']}(x:{w['x']},y:{w['y']})" for w in p.get('sen_details', [])])
            if not sen_log_str: sen_log_str = "Ninguno"

            # Death Vision Summary
            deaths_vision_summary = "Muertes sin visión: "
            no_vision_list = [f"{d['time']}m" for d in p.get('deaths_with_vision', []) if not d['has_vision']]
            if no_vision_list:
                deaths_vision_summary += ", ".join(no_vision_list)
            else:
                deaths_vision_summary += "Ninguna (Buen posicionamiento/visión)"

            deep_info = [
                f"  > Combat Extra: {p['stuns']}s stun, {p['buybacks']} buybacks, Wards: {p['obs_placed']}/{p['sen_placed']}",
                f"  > Líneas (10m): {p['lh_at_10']} LH, {p['dn_at_10']} DN, {p['gold_at_10']} Oro | Eficiencia: {p['laning_efficiency']}%",
                f"  > Timings Clave: {timing_summary}",
                f"  > Visión Detallada (Minuto/Coord): Obs [{obs_log_str}] | Sen [{sen_log_str}]",
                f"  > {deaths_vision_summary}",
                f"  > Habilidades (1-10): {', '.join(p['ability_build'][:10])}"
            ]
            context.append("\n".join(deep_info))
    
    if deep_mode and data.get("teamfights"):
        context.append("\n--- ANÁLISIS DE PELEAS (TEAMFIGHTS) ---")
        # List top 5 fights by deaths
        sorted_fights = sorted(data["teamfights"], key=lambda x: x["deaths"], reverse=True)[:5]
        
        for tf in sorted_fights:
            tf_summary = f"PELEA @ {tf['start']}m - {tf['end']}m (Muertes: {tf['deaths']})"
            
            # Simple summary of abilities used in this fight
            abilities_in_fight = []
            for player_tf in tf["players_involved"]:
                # We don't have the player name easily linked here without index logic, 
                # but we can list key abilities used in the fight overall.
                for ab, count in player_tf["abilities_used"].items():
                    if "attack" not in ab and count > 0: # Filter basic attacks
                        abilities_in_fight.append(ab)
            
            # Deduplicate and limit
            abilities_in_fight = list(set(abilities_in_fight))[:8] 
            
            if abilities_in_fight:
                tf_summary += f" | Habilidades Clave: {', '.join(abilities_in_fight)}"
                
            context.append(tf_summary)

    # 4. Draft & Objectives (New sections)
    if deep_mode:
        context.append("\n--- DRAFT (Picks & Bans) ---")
        picks_bans = meta.get("picks_bans", [])
        for pb in picks_bans:
            action = "PICK" if pb.get("is_pick") else "BAN"
            hero_info = hero_names.get(pb.get("hero_id"), {})
            h_name = hero_info.get("localized_name", f"Hero {pb.get('hero_id')}")
            context.append(f"  > {action}: {h_name} (Order: {pb.get('order')})")

        context.append("\n--- OBJETIVOS ---")
        objectives = meta.get("objectives", [])
        for obj in objectives:
            o_type = obj.get("type", "unknown")
            o_time = obj.get("time", 0) // 60
            if o_type in ["CHAT_MESSAGE_ROSHAN_KILL", "CHAT_MESSAGE_TOWER_KILL", "building_kill"]:
                context.append(f"  > {o_type.replace('CHAT_MESSAGE_', '')} @ {o_time}m")

    return "\n".join(context)

def get_player_info(account_id: str) -> Dict:
    """
    Fetches player profile information (name, avatar, rank) from OpenDota.
    """
    url = f"{OPENDOTA_API_URL}/players/{account_id}"
    try:
        print(f"[FETCH] Fetching profile for account {account_id}...")
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"error": f"Player {account_id} not found."}
        
        data = response.json()
        profile = data.get("profile", {})
        
        if not profile:
            return {"error": "Profile is private or does not exist."}
            
        return {
            "account_id": account_id,
            "personaname": profile.get("personaname"),
            "avatar": profile.get("avatarfull"),
            "rank_tier": data.get("rank_tier"), # Rank number (e.g. 71 for Divine 1)
            "leaderboard_rank": data.get("leaderboard_rank"),
            "plus": profile.get("plus")
        }
    except Exception as e:
        return {"error": str(e)}

def get_recent_matches(account_id: str) -> List[Dict]:
    """
    Fetches the last 20 matches for a given 32-bit Account ID using OpenDota API.
    
    Args:
        account_id: Dota 2 Friend ID (32-bit).
        
    Returns:
        List of formatted matches with match_id, hero, result, and KDA.
    """
    url = f"{OPENDOTA_API_URL}/players/{account_id}/matches?limit=20"
    
    try:
        print(f"[FETCH] Fetching last 20 matches for account {account_id}...")
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            return {"error": f"OpenDota API error: {response.status_code}"}
        
        matches = response.json()
        
        if not isinstance(matches, list):
            return {"error": "Could not retrieve matches. Profile may be private or invalid."}

        hero_names = get_hero_names()
        formatted_matches = []
        
        for m in matches:
            hero_id = m.get("hero_id")
            hero_data = hero_names.get(hero_id)
            
            # Defensive check if hero_data is a string (old cache format)
            if isinstance(hero_data, str):
                hero_name = hero_data
                hero_img_name = "abaddon" # Fallback
            elif isinstance(hero_data, dict):
                hero_name = hero_data.get("localized_name", f"Hero {hero_id}")
                hero_img_name = hero_data.get("name", "").replace("npc_dota_hero_", "")
            else:
                hero_name = f"Hero {hero_id}"
                hero_img_name = "abaddon"

            # OpenDota match result: player_slot 0-127 is Radiant, 128-255 is Dire
            is_radiant = m.get("player_slot", 0) < 128
            radiant_win = m.get("radiant_win")
            win = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)
            
            formatted_matches.append({
                "match_id": str(m.get("match_id")),
                "hero": hero_name,
                "hero_img": hero_img_name,
                "result": "Win" if win else "Loss",
                "kda": f"{m.get('kills', 0)}/{m.get('deaths', 0)}/{m.get('assists', 0)}",
                "start_time": m.get("start_time"),
                "duration": f"{m.get('duration', 0) // 60}m"
            })
            
        return formatted_matches
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch recent matches: {e}")
        return {"error": str(e)}

def refresh_player_data(account_id: str) -> Dict:
    """
    Triggers a manual refresh of player data on OpenDota.
    Useful after turning on 'Expose Public Match Data'.
    """
    url = f"{OPENDOTA_API_URL}/players/{account_id}/refresh"
    try:
        print(f"[REFRESH] Requesting update for player {account_id}...")
        response = requests.post(url, timeout=10)
        return {"status": "success", "detail": "Refresh requested. Please wait 1-2 minutes."}
    except Exception as e:
        return {"error": str(e)}

