import time
import asyncio
from typing import Dict, Optional
import json
from services.ai_coach import oracle
from knowledge.meta_740c import PATCH_CORE_CONCEPTS, TIER_S_ITEMS, COMMON_MISTAKES

class LiveCoachManager:
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {} # token -> session_data
        
        # Cooldowns and history to prevent spam
        self.last_advice_time: Dict[str, float] = {} 
        self.inventory_history: Dict[str, Dict] = {} 
        self.health_history: Dict[str, bool] = {} 

        # TIMING CONSTANTS (Time in seconds)
        self.TIMINGS = {
            "LOTUS": 180,      # Every 3 mins
            "BOUNTY": 180,     # Every 3 mins
            "POWER": 120,      # Every 2 mins (starting at 6:00)
            "WISDOM": 420,     # Every 7 mins
            "TORMENTOR": 1200, # At 20:00
        }
        
    def register_session(self, token: str, user_id: str = None):
        self.active_sessions[token] = {
            "start_time": time.time(),
            "last_gsi_update": 0,
            "hero": None,
            "user_id": user_id,
            "question_count": 0,
            "warned_timings": set(),
            "hero_alive": True,
            "low_hp_warned": False,
            "last_items_hash": "",
            "last_item_change_time": time.time(),
            "gold_warning_level": 0,
            "has_aegis": False,
            "aegis_pickup_time": 0,
            "last_periodic_advice_min": 0,
            "last_personal_advice_min": 0,
            "wards_seen": {},
            "welcomed": False,
            "observer_wards": 0,
            "sentry_wards": 0,
            "role": "Desconocido", # Pos 1-5
            "lane": "Desconocida"  # Safe/Mid/Off
        }
        print(f"[LIVE] New session registered: {token} (user: {user_id})")

    async def process_gsi_event(self, token: str, data: dict) -> Optional[dict]:
        if token not in self.active_sessions:
            self.register_session(token)
        
        session = self.active_sessions[token]

        # 0. HANDLE EXPLICIT QUESTION
        if data.get("type") == "question":
            # Removed limit check as per user request
            session["question_count"] = session.get("question_count", 0) + 1
            return await self._handle_question(data.get("text"), data, session)

        # 1. UNWRAP GSI DATA
        if data.get("type") == "gsi_event":
            data = data.get("data", {})

        # Only update snapshot if it's actual GSI data (not a custom type)
        session["last_snapshot"] = data
        session["last_gsi_update"] = time.time()

        current_time = time.time()
        map_data = data.get("map", {})
        game_time = map_data.get("clock_time", 0)
        is_paused = map_data.get("paused", False)

        if is_paused or game_time < 0:
            return None

        hero = data.get("hero", {})
        player = data.get("player", {})
        items = data.get("items", {})
        
        # 0.5 WELCOME MESSAGE (First time hero is detected)
        if not session["welcomed"] and hero.get("name"):
            session["welcomed"] = True
            session["hero"] = hero.get("name")
            session["role"] = self._detect_role(hero, items)
            
            # CONSUME TOKEN - This is a new match
            from services.token_service import token_service
            token = session.get("token")
            if token:
                # Use map.matchid as unique match identifier if available
                match_id = data.get("map", {}).get("matchid")
                result = token_service.consume_match(token, match_id)
                
                if result.get("success"):
                    matches_left = result.get("matches_remaining", 0)
                    print(f"[LIVE] Token consumed. Matches remaining: {matches_left}")
                    
                    # Warn user if running low on matches
                    if matches_left <= 2 and matches_left > 0:
                        session["low_matches_warning"] = True
                    elif matches_left == 0:
                        # Token depleted
                        return {
                            "type": "warning",
                            "text": "Tu token ha sido consumido. Esta es tu última partida con Oracle. Visita la web para comprar más partidas."
                        }
                else:
                    print(f"[LIVE] Failed to consume token: {result.get('error')}")
            
            return self._generate_welcome_message(hero, session)
        
        # 1. TIMING ALERTS (Runic, Lotus, Tormentor)
        alert = self._check_timings(game_time, session)
        if alert: return alert
        
        # 2. MASTER TACTICAL ADVICE (Every 5 min - Consolidated)
        master_advice = await self._check_master_advice(data, game_time, session)
        if master_advice: return master_advice

        # 2. ROSHAN / AEGIS LOGIC

        # 4. DEATH ANALYSIS
        was_alive = session.get("hero_alive", True)
        is_alive = hero.get("alive", True)
        
        if was_alive and not is_alive:
            session["hero_alive"] = False
            return await self._analyze_death(data, session)
        
        session["hero_alive"] = is_alive

        # 5. WARD DESTRUCTION DETECTION (Safe heuristic)
        ward_alert = self._check_wards(items, game_time, session)
        if ward_alert: return ward_alert

        # 6. CRITICAL HP WATCHER
        max_health = hero.get("max_health", 100)
        current_health = hero.get("health", 100)
        health_percent = (current_health / max_health) * 100 if max_health > 0 else 100
        
        if is_alive and health_percent < 25 and not session.get("low_hp_warned"):
            session["low_hp_warned"] = True
            return {"type": "warning", "text": "¡Vida crítica! Ten cuidado."}
        elif health_percent > 30:
            session["low_hp_warned"] = False

        return None
    
    def _generate_welcome_message(self, hero: dict, session: dict) -> dict:
        """Generates a personalized welcome message based on the hero."""
        hero_name = hero.get("name", "Unknown").replace("npc_dota_hero_", "").replace("_", " ").title()
        
        # Hero-specific compliments
        hero_compliments = {
            "ursa": "¡Ursa! Excelente elección. Domina Roshan y destruye carries.",
            "invoker": "¡Invoker! Un héroe de alto skill. Demuestra tu maestría.",
            "pudge": "¡Pudge! El carnicero. Tus hooks decidirán la partida.",
            "phantom assassin": "¡Phantom Assassin! Críticos devastadores te esperan.",
            "anti mage": "¡Anti-Mage! Farmea rápido y castiga a los casters.",
            "juggernaut": "¡Juggernaut! Versátil y letal. Buen pick.",
            "axe": "¡Axe! Iniciador implacable. Corta cabezas.",
            "crystal maiden": "¡Crystal Maiden! Soporte clave. Tu ultimate cambiará teamfights.",
            "lion": "¡Lion! Disables mortales. Elimina carries con tu Finger.",
            "earthshaker": "¡Earthshaker! Espera el momento perfecto para el Echo Slam."
        }
        
        hero_key = hero_name.lower()
        compliment = hero_compliments.get(hero_key, f"¡{hero_name}! Buena elección de héroe.")
        
        role_name = session.get("role", "Héroe")
        welcome_text = f"""Oracle activado. {compliment} Jugarás como {role_name}.
        
Funciones: Alertas de tiempos, consejos personales cada tres minutos, análisis de equipo cada cinco minutos. Presiona Ctrl para hablar conmigo."""
        
        return {"type": "advice", "text": welcome_text}

    def _detect_role(self, hero: dict, items: dict) -> str:
        """Simple heuristic to guess role based on hero name."""
        name = hero.get("name", "").replace("npc_dota_hero_", "")
        # Very basic DB - extend as needed
        pos1 = ["anti_mage", "juggernaut", "phantom_assassin", "ursa", "luna", "drow_ranger", "spectre", "faceless_void"]
        pos2 = ["invoker", "sf", "storm_spirit", "tinker", "queenofpain", "puck", "ember_spirit", "zeus"]
        pos3 = ["axe", "centaur", "tidehunter", "bristleback", "mars", "legion_commander", "slardar"]
        pos4 = ["pudge", "mirana", "earthshaker", "tusk", "rubick", "skywrath_mage"]
        pos5 = ["crystal_maiden", "lion", "witch_doctor", "dazzle", "oracle", "lich", "jakiro"]
        
        if name in pos1: return "Posición Uno (Hard Carry)"
        if name in pos2: return "Medio Juego (Midlaner)"
        if name in pos3: return "El Sufridor (Offlaner)"
        if name in pos4: return "Soporte (Posición 4)"
        if name in pos5: return "Soporte Duro (Posición 5)"
        return "Héroe"

    def _check_timings(self, game_time: int, session: dict) -> Optional[dict]:
        warning_window = 20
        # Check standard timings (Wisdom, Lotus, Power)
        # Use a window of 15 seconds for checks
        
        # Wisdom Runes (Every 7 min: 7, 14, 21...)
        t_wisdom = game_time + warning_window
        if t_wisdom > 300 and (t_wisdom % 420) < 15:
            key = f"wisdom_{ t_wisdom // 60 }"
            if key not in session["warned_timings"]:
                session["warned_timings"].add(key)
                return {"type": "advice", "text": "Runa de Sabiduría en veinte segundos. Asegúrala."}

        # Lotus Flowers (Every 3 min)
        t_lotus = game_time + warning_window
        if t_lotus > 60 and (t_lotus % 180) < 15:
            key = f"lotus_{ t_lotus // 60 }"
            if key not in session["warned_timings"]:
                session["warned_timings"].add(key)
                return {"type": "advice", "text": "Lotos en veinte segundos. Ve al estanque."}

        # Power Runes (Every 2 min starting at 6:00)
        t_power = game_time + warning_window
        if t_power >= 340 and (t_power % 120) < 15:
            key = f"power_{ t_power // 60 }"
            if key not in session["warned_timings"]:
                session["warned_timings"].add(key)
                return {"type": "advice", "text": "Runa de Poder en veinte segundos."}

        # Tormentor (At 20:00)
        if 1170 <= game_time <= 1200:
            key = "tormentor_20"
            if key not in session["warned_timings"]:
                session["warned_timings"].add(key)
                return {"type": "advice", "text": "Tormentores aparecen en veinte segundos. Reúne al equipo."}

        return None

    def _check_roshan_aegis(self, items: dict, game_time: int, session: dict) -> Optional[dict]:
        """Tracks Aegis presence and handles expiry warnings."""
        current_items = self._hash_items(items).lower()
        has_aegis_now = "aegis" in current_items
        
        # 1. Detection of Pickup
        if has_aegis_now and not session["has_aegis"]:
            session["has_aegis"] = True
            session["aegis_pickup_time"] = game_time
            return {"type": "advice", "text": "Aegis recogida. Tienes 5 minutos de inmortalidad."}
        
        # 2. Expiry Warning (30s before 5 mins)
        if session["has_aegis"]:
            time_held = game_time - session["aegis_pickup_time"]
            if 270 <= time_held <= 280 and not session.get("aegis_expiry_warned"):
                session["aegis_expiry_warned"] = True
                return {"type": "warning", "text": "¡Atención! La Aegis expira en 30 segundos."}
            
            if not has_aegis_now: # Aegis was either consumed or expired
                session["has_aegis"] = False
                session["aegis_expiry_warned"] = False
                # If game_time - pickup_time >= 300, it expired
                if game_time - session["aegis_pickup_time"] >= 300:
                    return {"type": "advice", "text": "La Aegis ha expirado de tu inventario."}
        
        return None

    async def _check_master_advice(self, data: dict, game_time: int, session: dict) -> Optional[dict]:
        """Consolidated Tactical Advice every 5 minutes (Master Plan)."""
        current_min = game_time // 60
        
        # Trigger window: Every 5 minutes, 0s-15s window.
        if current_min > 0 and current_min % 5 == 0 and (game_time % 300) < 15 and current_min != session.get("last_master_advice_min"):
            session["last_master_advice_min"] = current_min
            
            hero = data.get("hero", {})
            player = data.get("player", {})
            items = data.get("items", {})
            allplayers = data.get("allplayers", {}) or {}
            role = session.get("role", "Héroe")

            # 1. Personal Stats vs Benchmarks
            lh = player.get("last_hits", 0)
            dn = player.get("denies", 0)
            target_lh = current_min * 8 # Heuristic: 8 LH/min
            kills = player.get("kills", 0)
            deaths = player.get("deaths", 0)
            assists = player.get("assists", 0)
            gold = player.get("gold", 0)
            
            # 2. Team Context (Teammates KDA)
            player_slot = player.get("team_slot", 0)
            is_radiant = player_slot < 5
            allies_summary = []
            
            for slot, p_data in allplayers.items():
                try:
                    slot_num = int(slot)
                    if (slot_num < 128) == is_radiant: # Same team
                        # Skip self
                        if slot_num == player_slot: continue
                        name = p_data.get('name', 'Aliado').replace('npc_dota_hero_', '').replace('_', ' ').title()
                        allies_summary.append(f"{name}: {p_data.get('kills', 0)}/{p_data.get('deaths', 0)}/{p_data.get('assists', 0)}")
                except: continue

            # 3. Vision / Map Context
            obs_count = items.get("slot7", {}).get("charges", 0) if items.get("slot7", {}).get("name") == "item_ward_observer" else 0
            sent_count = items.get("slot8", {}).get("charges", 0) if items.get("slot8", {}).get("name") == "item_ward_sentry" else 0
            
            AI_PROMPT = f"""
            INFORME TÁCTICO MAESTRO - Minuto {current_min}
            
            DATOS DEL USUARIO:
            Héroe: {hero.get('name')} | Rol: {role}
            Estadísticas: {kills}/{deaths}/{assists} | Oro actual: {gold}
            Farm: {lh} Last Hits (Meta: {target_lh}), {dn} Denies.
            Inventario: {self._hash_items(items)}
            Wards en inventario: Observer={obs_count}, Sentry={sent_count}
            
            SITUACIÓN DEL EQUIPO:
            Aliados: {", ".join(allies_summary) if allies_summary else "No hay datos de aliados"}
            
            TAREA: Genera un PLAN MAESTRO detallado para los próximos 5 minutos.
            1. Evalúa el rendimiento del usuario (especialmente si es carry y tiene pocos last hits).
            2. Analiza el estado del equipo (¿quién está fuerte? ¿quién está regalando muertes?).
            3. Da 3 órdenes tácticas específicas (farming, pelea, presión, items).
            
            IMPORTANTE: Respuesta EXTENSA y DETALLADA. No uses markdown. No uses diminutivos.
            Tono: Coach Inmortal implacable y analítico. Idioma: Español.
            """

            try:
                resp = oracle.ask_oracle(AI_PROMPT, f"Master {current_min}", "LIVE_MASTER")
                return {"type": "advice", "text": resp}
            except Exception as e:
                print(f"[LIVE] Error in Master Advice: {e}")
            
        return None

    def _check_wards(self, items: dict, game_time: int, session: dict) -> Optional[dict]:
        """Very basic safe detection: if a ward item count drops unexpectedly? 
        Actually GSI sends ward count. If it drops and hero pos hasn't changed much, it was placed.
        But detecting it BROKEN (deward) requires checking vision? 
        Safety: Valve doesn't like auto-detection of enemy actions in fog.
        We will skip 'enemy ward detection' to stay safe as per user request.
        """
        return None

    async def _analyze_death(self, data: dict, session: dict) -> dict:
        hero = data.get("hero", {})
        player = data.get("player", {})
        items = data.get("items", {})
        game_time = data.get("map", {}).get("clock_time", 0)
        
        ai_prompt = f"""
        CONTEXTO: Muerte en minuto {game_time//60}. Hero: {hero.get('name')} | Oro: {player.get('gold')}
        Items: {self._hash_items(items)}
        ¿Por qué murió? Sugiere un item de contra (parche 7.40). 
        Máximo 20 palabras. Español. Coach Inmortal. NO USES DIMINUTIVOS (di minutos, segundos).
        """
        try:
            ai_response = oracle.ask_oracle(context=ai_prompt, user_question="Veredicto muerte", match_id="LIVE_DEATH")
            return {"type": "advice", "text": ai_response.replace("*", "")}
        except:
            return {"type": "advice", "text": "Analiza tu posicionamiento. Compra un item defensivo del parche."}

    async def _handle_question(self, question: str, data: dict, session: dict) -> dict:
        snapshot = session.get("last_snapshot", {})
        hero = snapshot.get("hero", {})
        player = snapshot.get("player", {})
        allplayers = snapshot.get("allplayers", {})
        
        # If no snapshot, it means no game started or GSI not sending data
        if not hero and not player:
            context = "EL USUARIO ESTÁ EN EL MENÚ O SIN PARTIDA ACTIVA. Responde como un Coach que espera el inicio para dar órdenes."
        else:
            # Add basic context about allies for the AI to answer "how is my team doing?"
            allies_info = []
            if isinstance(allplayers, dict):
                for slot, p in allplayers.items():
                    allies_info.append(f"{p.get('name', 'Héroe')}: KDA {p.get('kills', 0)}/{p.get('deaths', 0)}")
            
            game_min = snapshot.get('map', {}).get('clock_time', 0) // 60
            context = f"""
            PARTIDA EN VIVO - Minuto {game_min}.
            Héroe: {hero.get('name', 'Desconocido')} | Rol: {session.get('role', 'Desconocido')}
            KDA: {player.get('kills',0)}/{player.get('deaths',0)}/{player.get('assists',0)}
            Allies: {', '.join(allies_info[:4])}
            Items: {self._hash_items(snapshot.get('items', {}))}
            """
        
        try:
            # Use oracle to get answer
            answer = oracle.ask_oracle(f"CONTEXTO: {context}\nPREGUNTA DEL USUARIO: {question}", question, "LIVE_QA")
            # Remove MD characters just in case
            clean_answer = answer.replace("*", "").replace("#", "").replace("_", "")
            return {"type": "answer", "text": clean_answer}
        except Exception as e:
            print(f"[QA ERROR] {e}")
            return {"type": "answer", "text": "El Oráculo está meditando. Intenta de nuevo en unos segundos."}

    def _hash_items(self, items: dict) -> str:
        names = []
        for i in range(9):
            slot = items.get(f"slot{i}", {})
            name = slot.get("name", "empty").replace("item_", "")
            if name != "empty": names.append(name)
        return ", ".join(names)

live_manager = LiveCoachManager()
