import os
from typing import Optional, Dict, List
from dotenv import load_dotenv
from openai import OpenAI
import time

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
    print("[ORACLE] RAG 2.0 (FAISS) activo - Búsqueda semántica disponible")
except Exception as e:
    # Fallback silencioso si no hay índice
    RAG_V2_ENABLED = False
    if "index" not in str(e).lower():
        print(f"[ORACLE] Warning: RAG 2.0 no disponible: {e}")

load_dotenv()

class OracleCoach:
    def __init__(self):
        # Configuración del cliente OpenRouter / OpenAI
        api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        # Lista de modelos priorizada (VALIDADA FEB 2026)
        # IDs extraídos de documentación oficial de OpenRouter
        # Lista de modelos CORREGIDA y LIMPIA
        self.available_models = [
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "deepseek/deepseek-r1:free",
        ]
        
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
        Envía contexto y pregunta a OpenRouter.
        RAG se ejecuta SIEMPRE en cada mensaje.
        Incluye sistema de fallo y reintento (fallback) entre modelos.
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
                    pass
            except Exception as e:
                print(f"[RAG] ❌ Error al obtener conocimiento: {e}")
        
        # ===== RAG 2.0: SEMANTIC INJECTION =====
        semantic_injection = ""
        if RAG_V2_ENABLED:
            try:
                # Semantic search for additional context
                semantic_knowledge = rag_v2.search(user_question, top_k=3)
                if semantic_knowledge:
                    semantic_injection = f"\n\n📖 CONOCIMIENTO SEMÁNTICO (Habilidades/Items):\n{semantic_knowledge}\n"
            except Exception as e:
                if debug:
                    print(f"[RAG 2.0] ❌ Error en búsqueda semántica: {e}")

        # ===== CONSTRUCCIÓN DE MENSAJES =====
        prompt = f"{knowledge_injection}{semantic_injection}CONTEXTO DE PARTIDA:\n{context}\n\nPREGUNTA DEL USUARIO: {user_question}"
        
        messages = [{"role": "system", "content": self.system_instruction}]
        
        # Usamos historial externo si existe, sino local
        if external_history:
             messages.extend(external_history[-4:])
        elif match_id and match_id in self.histories_by_match:
            history = self.histories_by_match[match_id][-4:]
            messages.extend(history)
        
        messages.append({"role": "user", "content": prompt})

        # ===== CONSULTA A API (CON FALLBACKS) =====
        last_error = ""
        
        for model in self.available_models:
            try:
                if debug:
                    print(f"[ORACLE] 🚀 Consultando {model}...") 
                
                start_time = time.time()
                
                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "Oracle Dota AI Coach",
                    },
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024,
                )
                
                duration = time.time() - start_time
                answer = completion.choices[0].message.content
                
                print(f"[ORACLE] ✅ Éxito con {model} ({duration:.2f}s)")
                return self._finalize_response(match_id, user_question, answer)
                
            except Exception as e:
                error_msg = str(e)
                print(f"[ORACLE] ⚠️ Falló {model}: {error_msg}")
                last_error = error_msg
                # Continúa loop al siguiente modelo
        
        return f"El Oráculo intentó invocar a todos los espíritus, pero fallaron. Error final: {last_error}"

    def _finalize_response(self, match_id: str, user_question: str, answer_text: str) -> str:
        if match_id:
            if match_id not in self.histories_by_match:
                self.histories_by_match[match_id] = []
            self.histories_by_match[match_id].append({"role": "user", "content": user_question})
            self.histories_by_match[match_id].append({"role": "assistant", "content": answer_text})
            # Mantener historia corta para ahorrar tokens
            if len(self.histories_by_match[match_id]) > 8:
                self.histories_by_match[match_id] = self.histories_by_match[match_id][-8:]
        return answer_text

# Singleton
oracle = OracleCoach()
