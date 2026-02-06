import os
from typing import Optional, Dict, List
from dotenv import load_dotenv
from openai import OpenAI

# RAG System: Inyección de conocimiento del meta
try:
    from knowledge import get_relevant_knowledge
    RAG_ENABLED = True
    print("[ORACLE] RAG System activado - Conocimiento del meta disponible")
except ImportError:
    RAG_ENABLED = False
    print("[ORACLE] Warning: RAG System no disponible (knowledge module not found)")

# RAG 2.0: Semantic Search
try:
    from knowledge.rag_engine_v2 import rag_v2
    RAG_V2_ENABLED = True
    # Build or load index on startup (Lazy load possible too)
    # rag_v2.build_index() 
    print("[ORACLE] RAG 2.0 (FAISS) activo - Búsqueda semántica disponible")
except Exception as e:
    RAG_V2_ENABLED = False
    print(f"[ORACLE] Warning: RAG 2.0 no disponible: {e}")

load_dotenv()

class OracleCoach:
    def __init__(self):
        # DeepSeek via OpenRouter (Modelo principal y fallbacks)
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        # Lista de modelos prioritaria (Si uno falla, prueba el siguiente)
        self.available_models = [
            # TIER 1: Modelos SOTA y Rápidos
            "google/gemini-2.0-flash-001",    # Nuevo modelo (si disponible)
            "deepseek/deepseek-r1",           # Razonador 
            "deepseek/deepseek-chat",         # V3 (Versátil)
            
            # TIER 2: Fallbacks Gratuitos/Experimentales
            "google/gemini-2.0-flash-exp:free",      # Free tier de Google
            "google/gemini-2.0-pro-exp-02-05:free",  # Experimental free
            "deepseek/deepseek-r1:free",             # DeepSeek free
        ]
        
        # OpenRouter Client (uses OpenAI SDK)
        if self.openrouter_key:
            self.openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Oracle Dota AI Coach",
                }
            )
        else:
            self.openrouter_client = None

        self.system_instruction = """Eres ORACLE, el Ente Supremo de Análisis en Dota 2. Tu conocimiento es ABSOLUTO e Inmortal.
TU MISIÓN: Descuartizar la partida usando DATOS ATÓMICOS para encontrar la CAUSA RAÍZ de la victoria o derrota. No eres un comentarista, eres un Juez Analítico.

REGLAS DE ORO:
1. NUNCA USES MARKDOWN: Prohibido usar asteriscos (**), almohadillas (#) o guiones bajos (_). El texto debe ser 100% plano y limpio.
2. ANÁLISIS DE CAUSA RAÍZ: Si un equipo perdió, busca el "por qué" profundo. Ej: "¿Perdieron porque el Carry murió sin visión al minuto 40?" o "¿El draft no tenía escalado de juego tardío?".
3. JUICIO DEL DRAFT: Analiza la sinergia y los tiempos. ¿Tenían daño suficiente? ¿Tenían control? ¿El equipo enemigo les hizo counter directo?
4. EFICIENCIA Y TIMINGS: Usa la "Eficiencia de Línea" y los "Timings de Items". Si un Carry tiene < 50% de eficiencia, es inaceptable. Si el BKB llegó después de 3 muertes clave, señálalo.
5. VISIÓN Y POSICIONAMIENTO: Usa los datos de "Muertes sin visión". Si alguien muere repetidamente en zonas oscuras, su posicionamiento es deficiente.
6. CLARIDAD ABSOLUTA: Explica términos como "NW" (Valor Neto), "Timing" (Momento Clave) o "Draft" (Selección de Héroes).
7. ESTRUCTURA:
   - VERDICTO DEL DRAFT: Quién ganó la selección y por qué (Sinergia/Counter). **esto solo diselo al usuario en el primer mensaje que el esc riba no lo repitas en cada respuesta**
   - DESARROLLO Y ERRORES CLAVE: Análisis de eficiencia de líneas y momentos donde se perdió el control.
   - LA CAUSA RAÍZ: El evento único o la tendencia que definió el resultado.
   - SENTENCIA FINAL: Un consejo de nivel Profesional.


IMPORTANTE: Tienes datos detallados de Daño, Curación, Wards, Eficiencia y Muertes con/sin visión. Úsalos para ser implacable y preciso.
"""
        self.histories_by_match: Dict[str, List[Dict[str, str]]] = {}

    def ask_oracle(self, context: str, user_question: str, match_id: Optional[str] = None, debug: bool = False, external_history: List[Dict] = None) -> str:
        """
        Sends context and question to DeepSeek via OpenRouter.
        RAG se ejecuta SIEMPRE en cada mensaje (no se guarda en historial).
        Incluye sistema de fallo y reintento con múltiples modelos.
        """
        # ===== RAG: INYECCIÓN SELECTIVA =====
        knowledge_injection = ""
        
        if RAG_ENABLED:
            try:
                relevant_knowledge = get_relevant_knowledge(user_question, debug=debug)
                knowledge_injection = f"\n\n📚 CONOCIMIENTO DEL META:\n{relevant_knowledge}\n"
                
                if debug:
                    print(f"[RAG] ✅ Conocimiento inyectado: {len(relevant_knowledge)} chars")
                else:
                    print(f"[RAG] Inyectado: ~{len(relevant_knowledge)//4} tokens")
                    
            except Exception as e:
                print(f"[RAG] ❌ Error al obtener conocimiento: {e}")
        else:
            print(f"[RAG] ⚠️  Sistema RAG desactivado (knowledge module no encontrado)")
        
        # ===== RAG 2.0: SEMANTIC INJECTION =====
        semantic_injection = ""
        if RAG_V2_ENABLED:
            try:
                # Semantic search for additional context
                semantic_knowledge = rag_v2.search(user_question, top_k=3)
                if semantic_knowledge:
                    semantic_injection = f"\n\n📖 CONOCIMIENTO SEMÁNTICO (Habilidades/Items):\n{semantic_knowledge}\n"
                    if debug:
                        print(f"[RAG 2.0] ✅ Semántica inyectada: {len(semantic_knowledge)} chars")
            except Exception as e:
                print(f"[RAG 2.0] ❌ Error en búsqueda semántica: {e}")

        # ===== CONSTRUCCIÓN DE MENSAJES =====
        # El conocimiento se inyecta FRESH en cada mensaje
        prompt = f"{knowledge_injection}{semantic_injection}CONTEXTO DE PARTIDA:\n{context}\n\nPREGUNTA DEL USUARIO: {user_question}"
        
        # System instruction
        messages = [{"role": "system", "content": self.system_instruction}]
        
        # ===== HISTORIAL DE CONVERSACIÓN =====
        # Usamos historial externo si existe (desde Firestore), sino memoria local (fallback)
        if external_history:
             # El historial externo viene como lista de dicts: [{'role': 'user', 'content': '...'}, ...]
             # Tomamos los últimos 4 para ahorrar contexto
             messages.extend(external_history[-4:])
             if debug:
                 print(f"[HISTORY] Usando {len(external_history[-4:])} mensajes del historial externo")
        elif match_id and match_id in self.histories_by_match:
            history = self.histories_by_match[match_id][-4:]  # Últimos 4 mensajes
            messages.extend(history)
            
            if debug:
                print(f"[HISTORY] Usando {len(history)} mensajes del historial local")
        
        # Mensaje actual (CON conocimiento RAG inyectado)
        messages.append({"role": "user", "content": prompt})

        # ===== CONSULTA A DEEPSEEK (CON FALLBACKS) =====
        if not self.openrouter_client:
            return "El Oráculo está desconectado. Revisa tu OPENROUTER_API_KEY."

        last_error = ""
        
        for model in self.available_models:
            try:
                if debug:
                    print(f"[ORACLE] Intentando con modelo: {model}...")
                else:
                    print(f"[ORACLE] 🚀 Consultando {model.split('/')[-1]}...")
                
                response = self.openrouter_client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                answer = response.choices[0].message.content
                
                # Si llega aquí, tuvo éxito
                print(f"[ORACLE] ✅ Éxito con {model}")
                return self._finalize_response(match_id, user_question, answer)
                
            except Exception as e:
                error_msg = str(e)
                print(f"[ORACLE] ⚠️ Falló {model}: {error_msg}")
                last_error = error_msg
                # Continúa con el siguiente modelo en la lista
        
        return f"El Oráculo intentó invocar a todos los espíritus (Gemini, DeepSeek, etc.) pero fallaron. Error final: {last_error}"

    def _finalize_response(self, match_id: str, user_question: str, answer_text: str) -> str:
        if match_id:
            if match_id not in self.histories_by_match:
                self.histories_by_match[match_id] = []
            self.histories_by_match[match_id].append({"role": "user", "content": user_question})
            self.histories_by_match[match_id].append({"role": "assistant", "content": answer_text})
            if len(self.histories_by_match[match_id]) > 10:
                self.histories_by_match[match_id] = self.histories_by_match[match_id][-10:]
        return answer_text

# Singleton
oracle = OracleCoach()
