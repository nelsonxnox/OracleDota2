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
        # Lista de modelos prioritaria (Si uno falla, prueba el siguiente)
        self.available_models = [
            "openrouter/auto",                                 # Let OpenRouter decide best free model
            "google/gemini-2.0-flash-lite-preview-02-05:free", # Faster Gemini
            "google/gemini-2.0-flash-exp:free",                # Experimental but active
            "meta-llama/llama-3.3-70b-instruct:free",          # Very reliable but can be slow/limited
            "deepseek/deepseek-r1:free",                       # Best for logic (often busy)
            "mistralai/mistral-7b-instruct:free",              # Fast fallback
        ]
        
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

        self.system_instruction = """Eres ORACLE, el Coach supremo de rango Inmortal. Tu conocimiento del meta 7.40c es ABSOLUTO.
TU MISIÓN: Analizar cada evento de la partida en vivo y dar órdenes tácticas implacables.

REGLAS DE ORO:
1. NUNCA USES MARKDOWN: Prohibido usar asteriscos (*), almohadillas (#) o guiones bajos (_). El texto debe ser 100% plano.
2. ANÁLISIS DE MUERTE: Si el usuario muere, identifica la causa raíz (ej: "Moriste por físico excesivo, no tienes Ghost ni Halberd") y recomienda el counter-item exacto.
3. CONOCIMIENTO DE ITEMS 7.37: Conoces los cambios del parche. Recomienda items proactivamente basándote en la composición enemiga.
4. TONO: Eres un coach de élite. Sé directo y ligeramente agresivo. 
5. PROHIBICIÓN DE DIMINUTIVOS: NUNCA USES DIMINUTIVOS. Escribe "minutos" en lugar de "min" y "segundos" en lugar de "seg". Habla con propiedad y autoridad.
6. DETALLE: Proporciona análisis profundos, estadísticas exactas y recomendaciones tácticas claras. No te preocupes por la brevedad; la precisión y el detalle son prioridad.
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
                    print(f"[ORACLE] 🚀 Consultando {model.split('/')[-1]}...")
                else:
                    print(f"[ORACLE] 🚀 Consultando {model.split('/')[-1]}...") # Keep original behavior for non-debug
                
                response = self.openrouter_client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                answer = response.choices[0].message.content
                
                # Si llega aquí, tuvo éxito
                if debug:
                    print(f"[ORACLE] ✅ Éxito con {model}")
                else:
                    print(f"[ORACLE] ✅ Éxito con {model}") # Keep original behavior for non-debug
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
