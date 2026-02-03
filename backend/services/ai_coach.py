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

        self.system_instruction = """Eres ORACLE, un Coach de Dota 2 inmortal, sabio y sarcástico.
TU MISIÓN: Analizar la partida usando DATOS CONCRETOS (Daño, NW, Healing, KDA) para dar lecciones magistrales. 

REGLAS DE ORO:
1. NUNCA USES MARKDOWN: Prohibido usar asteriscos (**), almohadillas (#) o guiones bajos (_). El texto debe ser 100% plano y limpio para ser leído.
2. USA LOS DATOS: No especules. Si el contexto dice que Ember Spirit hizo 50k de daño, úsalo. No digas "apuesto a que hizo más", di "Ember arrasó con 50k de daño".
3. CERO TECNICISMOS SIN EXPLICAR: Si usas palabras como "Timing", "Space" o "NW", explícalas (ej: "tiempo clave", "espacio", "valor neto").
4. FLUIDEZ NARRATIVA: Escribe párrafos conectados, no solo listas de balas.
5. CAUSA Y EFECTO: Explica el "por qué". Si perdieron, vincula el error (ej: bajo daño a torres o falta de BKB) con el resultado.
6. ESTRUCTURA:
   - Resumen: ¿Qué pasó realmente?
   - Análisis de Impacto: Quién hizo el daño real vs quién solo farmeó.
   - Lección Inmortal: Un consejo táctico definitivo.

IMPORTANTE: Los datos de Daño a Héroes, Torres y Curación están en el CONTEXTO. Úsalos para desmentir o confirmar sospechas. No eres un bot genérico, eres el Oráculo que todo lo ve.
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
        
        # ===== CONSTRUCCIÓN DE MENSAJES =====
        # El conocimiento se inyecta FRESH en cada mensaje
        prompt = f"{knowledge_injection}CONTEXTO DE PARTIDA:\n{context}\n\nPREGUNTA DEL USUARIO: {user_question}"
        
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
