import time
import asyncio
from typing import Dict, Optional
import json
from services.ai_coach import oracle
from knowledge.meta_737 import PATCH_CORE_CONCEPTS, TIER_S_ITEMS, COMMON_MISTAKES

class LiveCoachManager:
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {} # token -> session_data
        
        # Cooldowns to prevent spam
        self.last_advice_time: Dict[str, float] = {} 
        self.inventory_history: Dict[str, Dict] = {} # token -> {last_check_time, items_hash}
        self.health_history: Dict[str, bool] = {} # token -> was_low_hp

        
    def register_session(self, token: str, user_id: str = None):
        self.active_sessions[token] = {
            "start_time": time.time(),
            "last_gsi_update": 0,
            "hero": None,
            "gold_warning_sent": False,
            "user_id": user_id  # Track which user owns this session
        }
        print(f"[LIVE] New session registered: {token} (user: {user_id})")

    async def process_gsi_event(self, token: str, data: dict) -> Optional[dict]:
        """
        Analiza el estado del juego y retorna una respuesta de audio/texto si es necesario.
        Retorna None si no hay nada que decir.
        """
        if token not in self.active_sessions:
            self.register_session(token) # Auto-register if missing

        session = self.active_sessions[token]
        
        # Guardar snapshot más reciente para preguntas
        session["last_snapshot"] = data
        
        # Check explicit question
        if data.get("type") == "question":
            return await self._handle_question(data.get("text"), data, session)

        current_time = time.time()

        game_time = data.get("map", {}).get("clock_time", 0) # Segundos de juego
        
        # Actualizar estado
        session["last_gsi_update"] = current_time
        hero = data.get("hero", {})
        player = data.get("player", {})
        items = data.get("items", {})

        response = None

        # 1. EVENTO MUERTE (Proactivo)
        # Detectamos la transición de vivo a muerto
        was_alive = session.get("hero_alive", True)
        is_alive = hero.get("alive", True)
        
        if was_alive and not is_alive:
            # El héroe acaba de morir - ANÁLISIS PROFUNDO CON IA
            # No bloqueamos el websocket principal (idealmente), pero por simplicidad usamos await aquí.
            # edge-tts es rápido, pero la LLM puede tardar. 
            # Estrategia: Mandar audio inmediato "Analizando fallo..." y luego el veredicto?
            # Por ahora, mandamos directo al IA.
            
            hero_name = hero.get("name", "Unknown")
            kda = f"{player.get('kills')}/{player.get('deaths')}/{player.get('assists')}"
            gold = player.get("gold")
            
            ai_prompt = f"""
            Actúa como un coach de rango Inmortal severo. El usuario acaba de morir.
            Hero: {hero_name} | KDA: {kda} | Gold: {gold} | Tiempo: {game_time//60}min.
            Inventario: {self._hash_items(items)}
            
            Analiza el error fatal. Si tenía BKB/Mekansm y murió con ellos listos, sé sarcástico.
            Si murió sin visión, regáñalo. Si fue gank bajo runa, menciona el timing.
            RESPUESTA MÁXIMO 15 PALABRAS. INTIMIDANTE.
            """
            
            # Usamos ask_oracle (que llama a DeepSeek/Gemini)
            try:
                ai_response = oracle.ask_oracle(context=ai_prompt, user_question="Veredicto de muerte", match_id="LIVE_COACH")
                clean_text = ai_response.replace("*", "").replace("ERROR:", "").split("\n")[0]
            except:
                clean_text = "Has muerto. Concéntrate."
            
            response = {
                "type": "advice",
                "text": clean_text
            }
        session["hero_alive"] = is_alive
        
        if response: return response

        # 1.5. WATCHER DE VIDA (Combate Crítico)
        # Si HP < 20% y está vivo
        max_health = hero.get("max_health", 100)
        current_health = hero.get("health", 100)
        health_percent = (current_health / max_health) * 100 if max_health > 0 else 100
        
        if is_alive and health_percent < 25 and not session.get("low_hp_warned"):
            # Verificar BKB
            has_bkb_active = False # GSI generally doesn't send "active modifiers" easily without heavy config, 
                                   # but we can check if BKB is in inventory vs cooldown. 
                                   # For now, simplistic trigger:
            response = {"type": "warning", "text": "¡Vida crítica! Usa BKB o retrocede ahora."}
            session["low_hp_warned"] = True
            # Reset warning flag after 30 seconds or if health goes up
        elif health_percent > 30:
            session["low_hp_warned"] = False

        if response: return response

        # 2. MACRO REMINDERS (Solo si no está muerto)
        if is_alive:
            # Runas de Sabiduría (6:50, 13:50, 20:50)
            # 6:50 = 410s, 13:50 = 830s, 20:50 = 1250s
            if 405 <= game_time <= 415 and not session.get("wisdom_7_warned"):
                response = {"type": "advice", "text": "Atento. Runas de sabiduría en 10 segundos."}
                session["wisdom_7_warned"] = True
            
            elif 825 <= game_time <= 835 and not session.get("wisdom_14_warned"):
                response = {"type": "advice", "text": "Catorce minutos. Sabiduría y Tormentors en breve."}
                session["wisdom_14_warned"] = True

            elif 1245 <= game_time <= 1255 and not session.get("wisdom_21_warned"):
                response = {"type": "advice", "text": "Minuto 21. Runas de Sabiduría."}
                session["wisdom_21_warned"] = True
                
            # Tormentors (20:00 = 1200s)
            elif 1190 <= game_time <= 1200 and not session.get("tormentor_warned"):
                response = {"type": "advice", "text": "Minuto 20. Tormentors disponibles. Shard gratis."}
                session["tormentor_warned"] = True

        if response: return response

        # 3. GESTIÓN DE ORO (Gold > 4000 y estático)
        # Verificamos cada 10 segundos para no saturar
        if current_time - session.get("last_gold_check", 0) > 10:
            gold = player.get("gold", 0)
            if gold > 4000:
                # Comprobar si el inventario cambió
                current_items_hash = self._hash_items(items)
                last_items_hash = session.get("last_items_hash", "")
                last_change_time = session.get("last_item_change_time", current_time)

                if current_items_hash != last_items_hash:
                    session["last_items_hash"] = current_items_hash
                    session["last_item_change_time"] = current_time
                    session["gold_warning_level"] = 0
                else:
                    # Inventario estático
                    time_static = current_time - last_change_time
                    if time_static > 120 and session.get("gold_warning_level", 0) == 0: # 2 minutos
                        # ANÁLISIS DE ORO CON IA
                        hero_name = hero.get("name", "Unknown")
                        ai_prompt = f"""
                        Jugador {hero_name} tiene {gold} oro y no compra nada.
                        Inventario actual: {self._hash_items(items)}
                        Minuto: {game_time//60}
                        
                        Recomienda UN ITEM específico del Meta 7.37 que deba comprar YA.
                        Respuesta CORTA para TTS (Ej: "Compra BKB ya, tienes el oro").
                        """
                        
                        ai_response = oracle.ask_oracle(context=ai_prompt, user_question="Consejo de compra rápido", match_id="LIVE_COACH")
                        clean_text = ai_response.replace("*", "").split("\n")[0]
                        
                        response = {
                            "type": "warning", 
                            "text": clean_text
                        }
                        session["gold_warning_level"] = 1
            
            session["last_gold_check"] = current_time

        return response

    async def _handle_question(self, question: str, data: dict, session: dict) -> dict:
        """Maneja preguntas directas del usuario con contexto"""
        # Recuperar el último snapshot de GSI
        snapshot = session.get("last_snapshot", {})
        hero = snapshot.get("hero", {})
        player = snapshot.get("player", {})
        items = snapshot.get("items", {})
        
        context = f"""
        Hero: {hero.get("name")} | HP: {hero.get("health")}/{hero.get("max_health")} | Gold: {player.get("gold")}
        KDA: {player.get("kills")}/{player.get("deaths")}/{player.get("assists")}
        Inventario: {self._hash_items(items)}
        """
        
        ai_prompt = f"""
        El usuario pregunta: "{question}"
        Contexto del juego: {context}
        Responde como un Coach Inmortal. Breve, táctico y directo. Máximo 2 frases.
        """
        
        try:
            answer = oracle.ask_oracle(context=ai_prompt, user_question=question, match_id="LIVE_COACH_QA")
            clean_text = answer.replace("*", "").split("\n")[0]
        except:
            clean_text = "No puedo analizar eso ahora."
            
        return {"type": "answer", "text": clean_text}

    def _hash_items(self, items: dict) -> str:
        """Genera un hash simple del inventario para detectar cambios"""
        item_list = []
        for i in range(0, 9): # slots 0-5 inventory, 6-8 backpack
             item = items.get(f"slot{i}", {})
             item_list.append(item.get("name", "empty"))
        return ",".join(item_list)

live_manager = LiveCoachManager()
