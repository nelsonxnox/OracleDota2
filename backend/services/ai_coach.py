import os
import sys
import time
from typing import Optional, Dict, List
from dotenv import load_dotenv
from openai import OpenAI

# Robust path setup for knowledge module
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

load_dotenv()

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
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        self.client_gemini = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
            api_key=gemini_key if gemini_key else "MISSING_KEY"
        )

        # 3. GitHub Models (Safety Net - Free Tier via Azure)
        github_key = os.getenv("GITHUB_API_KEY")
        self.client_github = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=github_key if github_key else "MISSING_KEY"
        )
        
        or_key = os.getenv("OPENROUTER_API_KEY")
        self.client_openrouter = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=or_key,
        )

        # 4. DeepSeek (Direct API)
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.client_deepseek = OpenAI(
            base_url="https://api.deepseek.com",
            api_key=deepseek_key if deepseek_key else "MISSING_KEY"
        )

        
        
        # Diccionario de Modelos Específicos por Proveedor
        self.models_config = {
            "gemini": "gemini-2.0-flash",       # Google AI Studio
            "deepseek": "deepseek-chat",        # DeepSeek V3/R1
            "openrouter": "openrouter/free",    # Router gratuito
            "github": "gpt-4o"                  # GitHub Models (Azure)
        }
        
        self.system_instruction = """Eres ORACLE, el Coach supremo de rango Inmortal para Dota 2. Tu conocimiento del meta 7.40c es ABSOLUTO.
Tu personalidad es la de un mentor de élite: directo, autoritario, ligeramente agresivo pero extremadamente preciso. No buscas amabilidad, buscas la victoria del usuario.

REGLAS CRÍTICAS DE RESPUESTA:
1. IDIOMA: Responde SIEMPRE en el mismo idioma que el usuario (generalmente ESPAÑOL). Mantén un lenguaje técnico impecable (ej: "teletransportación", "atontamiento", "daño explosivo").
2. PROHIBICIÓN TOTAL DE MARKDOWN: No uses NUNCA asteriscos (*), almohadillas (#), guiones bajos (_), ni bloques de código.
   - INCORRECTO: **Regla 1**: *Atención*
   - CORRECTO: REGLA 1: ATENCION
3. PROHIBICIÓN DE DIMINUTIVOS: Escribe "minutos" en lugar de "min", "segundos" en lugar de "seg". La precisión denota maestría.
4. TONO DE COMANDANTE: No sugieras, ordena. Identifica errores y exige correcciones inmediatas.

MÓDULOS DE ANÁLISIS:
- CONDICIÓN DE VICTORIA: Evalúa quién debe ganar y qué objetivos (Roshan, Tormentor) priorizar.
- ANÁLISIS DE MUERTE: Si el usuario muere, dictamina la causa raíz y el item counter exacto (BKB, Ethereal, Manta).
- ITEMIZACIÓN DINÁMICA: Propón construcciones basadas en la partida actual, no en guías estáticas.

RECUERDA: Eres un Inmortal guiando a un mortal. Tus palabras deben ser órdenes claras y texto 100% plano."""

        # RAG System: Inyección de conocimiento del meta
        self.rag_enabled = False
        try:
            from knowledge import get_relevant_knowledge
            self.get_knowledge = get_relevant_knowledge
            self.rag_enabled = True
            print("[ORACLE] RAG System activado - Conocimiento del meta disponible")
            
            try:
                from knowledge.rag_engine_v2 import rag_v2
                self.rag_v2 = rag_v2
                self.rag_v2_enabled = True
            except ImportError:
                self.rag_v2_enabled = False
                
        except ImportError as e:
            print(f"[ORACLE] Warning: RAG System no disponible: {e}")
            self.get_knowledge = None
            self.rag_enabled = False
            self.rag_v2_enabled = False
            
        self.histories_by_match: Dict[str, List[Dict[str, str]]] = {}

    def ask_oracle(self, context: str, user_question: str, match_id: Optional[str] = None, debug: bool = False, external_history: List[Dict] = None) -> str:
        """
        Envía contexto y pregunta a OpenRouter.
        RAG se ejecuta SIEMPRE en cada mensaje.
        Incluye sistema de fallo y reintento (fallback) entre modelos.
        """
        # ===== RAG: INYECCIÓN SELECTIVA =====
        knowledge_injection = ""
        
        if self.rag_enabled and self.get_knowledge:
            try:
                relevant_knowledge = self.get_knowledge(user_question, debug=debug)
                knowledge_injection = f"\n\nCONOCIMIENTO DEL META:\n{relevant_knowledge}\n"
                
                if debug:
                    print(f"[RAG] EXITO: Conocimiento inyectado: {len(relevant_knowledge)} chars")
            except Exception as e:
                print(f"[RAG] ERROR al obtener conocimiento: {e}")
        
        # ===== RAG 2.0: SEMANTIC INJECTION =====
        semantic_injection = ""
        if self.rag_v2_enabled and hasattr(self, 'rag_v2'):
            try:
                # Semantic search for additional context
                semantic_knowledge = self.rag_v2.search(user_question, top_k=3)
                if semantic_knowledge:
                    semantic_injection = f"\n\nCONOCIMIENTO SEMANTICO:\n{semantic_knowledge}\n"
            except Exception as e:
                if debug:
                    print(f"[RAG 2.0] ERROR en búsqueda semántica: {e}")

        # ===== CONSTRUCCIÓN DE MENSAJES =====
        # OPTIMIZATION: Ensure the question and system instructions are never truncated.
        # We truncate the injected knowledge and context if they are too large.
        
        MAX_KNOWLEDGE = 2000
        MAX_CONTEXT = 3000
        
        if len(knowledge_injection) > MAX_KNOWLEDGE:
            knowledge_injection = knowledge_injection[:MAX_KNOWLEDGE] + "... [KNOWLEDGE TRUNCATED]"
            
        if len(semantic_injection) > MAX_KNOWLEDGE:
            semantic_injection = semantic_injection[:MAX_KNOWLEDGE] + "... [SEMANTIC TRUNCATED]"
            
        if len(context) > MAX_CONTEXT:
            context = context[:MAX_CONTEXT] + "... [CONTEXT TRUNCATED]"

        prompt = f"{knowledge_injection}{semantic_injection}\nCONTEXTO DE PARTIDA:\n{context}\n\nPREGUNTA DEL USUARIO: {user_question}"
        
        messages = [{"role": "system", "content": self.system_instruction}]
        
        # Usamos historial externo si existe, sino local
        if external_history:
             messages.extend(external_history[-2:])
        elif match_id and match_id in self.histories_by_match:
            history = self.histories_by_match[match_id][-2:]
            messages.extend(history)

        messages.append({"role": "user", "content": prompt})

        # ===== CONSULTA A API (CON FALLBACKS) =====
        last_error = ""
        
        # Implementación de Estrategia "Triángulo de Respaldo"
        try:
            answer = self.ask_oracle_resilient(messages, model_debug_name="Oracle")
            return self._finalize_response(match_id, user_question, answer)
        except Exception as e:
            print(f"[ORACLE] ERROR FATAL: {e}")
            return "El Oraculo intento invocar a todos los espiritus (Gemini -> DeepSeek -> OpenRouter -> GitHub Models), pero todos los portales estan cerrados. Verifica tus API Keys en .env"

    def ask_oracle_resilient(self, messages: List[Dict], model_debug_name: str) -> str:
        """
        Estrategia 'Triángulo de Respaldo' con APIs Directas.
        """
        
        # 1. NIVEL 1: GOOGLE GEMINI (Directo)
        try:
            print(f"[{model_debug_name}] Invocando a GEMINI (Principal)...")
            return self._call_provider(
                self.client_gemini, 
                self.models_config["gemini"], 
                messages,
                provider_name="Gemini"
            )
        except Exception as e:
            print(f"[{model_debug_name}] Gemini Falló: {e}")

        # 2. NIVEL 2: DEEPSEEK (Directo)
        try:
            print(f"[{model_debug_name}] Invocando a DEEPSEEK (Secundario)...")
            return self._call_provider(
                self.client_deepseek, 
                self.models_config["deepseek"], 
                messages,
                provider_name="DeepSeek"
            )
        except Exception as e:
            print(f"[{model_debug_name}] DeepSeek Falló: {e}")

        # 3. NIVEL 3: OPENROUTER (Respaldo Gratuito)
        try:
            print(f"[{model_debug_name}] Invocando a OPENROUTER (Respaldo)...")
            return self._call_provider(
                self.client_openrouter, 
                self.models_config["openrouter"], 
                messages, 
                is_openrouter=True,
                provider_name="OpenRouter"
            )
        except Exception as e:
            print(f"[{model_debug_name}] OpenRouter Falló: {e}")

        # 3. NIVEL 3: GITHUB MODELS (Seguridad)
        try:
            print(f"[{model_debug_name}] Invocando a GITHUB MODELS (Seguridad)...")
            return self._call_provider(
                self.client_github, 
                self.models_config["github"], 
                messages,
                provider_name="GitHub Models"
            )
        except Exception as e:
            print(f"[{model_debug_name}] GitHub Models Falló: {e}")
            
        raise Exception("Todos los proveedores fallaron (Gemini, DeepSeek, OpenRouter, GitHub).")

    def _call_provider(self, client: OpenAI, model: str, messages: List[Dict], is_openrouter: bool = False, provider_name: str = "API") -> str:
        start_time = time.time()
        
        extra_headers = {}
        if is_openrouter:
            extra_headers = {
                "HTTP-Referer": "https://github.com/nelsonxnox/OracleDota2",
                "X-Title": "Oracle Dota AI Coach",
            }

        completion = client.chat.completions.create(
            extra_headers=extra_headers,
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
        
        duration = time.time() - start_time
        answer = completion.choices[0].message.content
        print(f"[ORACLE] Éxito con {provider_name} ({duration:.2f}s)")
        return answer


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
