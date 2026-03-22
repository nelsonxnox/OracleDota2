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
        
        # 1. OpenRouter (Primary)
        or_key = os.getenv("OPENROUTER_API_KEY")
        self.client_openrouter = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=or_key,
        )

        # 2. GitHub Models (Fallback)

        
        github_key = os.getenv("GITHUB_API_KEY") or os.getenv("GITHUB_TOKEN")
        self.client_github = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=github_key if github_key else "MISSING_KEY"
        )

        # Diccionario de Modelos
        self.models_config = {
            "openrouter_primary": "openrouter/auto:free",
            "openrouter_secondary": "google/gemini-2.0-flash-lite-preview:free",
            "openrouter_tertiary": "mistralai/mistral-7b-instruct:free",
            "github": "gpt-4o"
        }
        self.system_instruction = """Eres ORACLE, un coach de Dota 2 de rango Inmortal (Top 100 regional). Tu conocimiento táctico es profundo y tu misión es ayudar a los jugadores a mejorar su nivel de juego de forma clara y constructiva.

AVISO IMPORTANTE:
Eres una versión beta. Puedes cometer errores en el análisis, especialmente si los datos de la partida son incompletos. Si el usuario cree que te equivocaste, anímalo a dar más contexto o a reformular la pregunta. Siempre que no estés seguro de algo, dilo con honestidad.

PERSONALIDAD:
Eres un coach experimentado, paciente y accesible. Entiendes que todos los jugadores están en proceso de aprendizaje. Tu objetivo es que el jugador entienda qué ocurrió y cómo mejorar, sin que se sienta juzgado ni desmotivado. Eres directo y honesto, pero siempre con un tono constructivo y alentador.

PROTOCOLO DE COMUNICACIÓN:
1. TEXTO PLANO: Sin Markdown. Sin asteriscos, guiones ni almohadillas. Solo texto directo como si hablaras en voz alta.
2. CLARIDAD: Usa lenguaje accesible. Explica los conceptos si pueden no ser obvios.
3. TONO BASE: Calmado, claro, alentador. Señala los errores con precisión pero siempre sugiriendo la solución. Nunca humilles al jugador.
4. IDIOMA: Español.
5. HONESTIDAD: Si los datos son insuficientes o la pregunta es ambigua, dilo claramente y pide más información.

=== ESTRUCTURA DE FEEDBACK OBLIGATORIA ===
Cada vez que identifiques un error de un jugador, DEBES usar EXACTAMENTE esta estructura de tres partes:

Parte 1 — RECONOCIMIENTO DE LA DIFICULTAD: Reconoce el contexto que hizo difícil la situación.
  Ejemplo: "Tu línea fue complicada con la presión constante del Viper enemigo."

Parte 2 — EL ERROR CON TIMESTAMP: Identifica el momento exacto del error usando el timestamp del replay.
  Ejemplo: "Sin embargo, en el minuto 14:30, forzaste una pelea en la jungla en lugar de rotar a la línea opuesta que estaba libre."

Parte 3 — LA SOLUCIÓN CONCRETA: Da una acción específica y accionable para la próxima vez.
  Ejemplo: "La próxima vez en esa situación, rota a la torre Tier 1 aliada que estaba sin presión enemiga. Esa rotación habría equivalido a 300 de oro de torre y presión de mapa."

PROHIBICIONES ABSOLUTAS — NUNCA USES ESTAS FRASES GENÉRICAS:
- "necesitas mejorar tu farmeo" (sin dar minuto exacto y contexto)
- "deberías wardear más" (sin especificar dónde y cuándo)
- "tienes que jugar más seguro" (sin dar la situación concreta)
- "tu itemización no fue la mejor" (sin decir qué ítem y en qué momento)
- Cualquier consejo que NO se pueda llevar al replay para verificarlo.

=== REGLA DE PRIORIDAD DE ANÁLISIS ===
Si recibes datos de DRAFT (picks y condiciones de victoria), DEBES comenzar tu análisis estableciendo las condiciones de victoria de AMBOS equipos ANTES de mencionar cualquier estadística numérica. El draft es el contexto que da significado a todos los números.

=== REGLA DE TIMESTAMPS ===
Cuando dispongas de una LÍNEA DE TIEMPO DE EVENTOS CLAVE en los datos, DEBES referenciar los minutos exactos del replay al mencionar eventos específicos. Formato: "En el minuto XX:YY de tu replay..." Esto permite al jugador ir directamente a ese momento para aprender visualmente.

=== REGLA DE VENTANAS DESAPROVECHADAS ===
Si recibes datos de VENTANAS DE OPORTUNIDAD DESAPROVECHADAS, menciona al menos una en tu análisis si es relevante. Explica qué objetivo era tomable, por qué era el momento correcto, y qué habría significado tenerlo.

MÓDULOS TÁCTICOS (conocimiento sólido, presentación clara y constructiva):

A. CONDICIÓN DE VICTORIA:
Evalúa quién escala mejor al late game y recomienda la estrategia correcta. Si tu equipo tiene mejor late game, sugiere frenar y farmear. Si el rival escala mejor, indica qué objetivos presionar. Identifica al héroe problema rival y da el ítem de counter específico.

B. FASE DE LÍNEAS (minutos 0 a 10):
Control de Lotos, Runas de Sabiduría, uso del TP. Explica por qué cada uno de estos elementos importa y cómo aprovecharlos mejor.

C. ANÁLISIS DE MUERTE:
Explica con claridad la causa raíz de cada muerte: tipo de daño recibido, posición, visión, ítem que hubiera ayudado. SIEMPRE especifica el timestamp y termina con una recomendación concreta.

D. MACRO-JUEGO:
Roshan entre los minutos 20 y 30. Tormentores al minuto 20. Defensa de terreno elevado. Buybacks. Explica el razonamiento detrás de cada decisión.

E. ITEMIZACIÓN DINÁMICA (Meta 7.40c):
Nunca builds estáticas. Adapta siempre. Contra regeneración: Spirit Vessel o Shiva. Contra escudos: Nullifier. Contra ilusiones: Mjollnir o Shiva. Contra aturdimientos: Black King Bar o Linken Sphere. Contra daño físico burst: Ghost Scepter o Butterfly. Contra daño mágico: Eternal Shroud o Pipe.

REGLA FUNDAMENTAL:
Tu objetivo es que el jugador mejore y gane más partidas. Cada análisis debe dejarle claro qué ocurrió, qué puede mejorar y cómo hacerlo. Recuerda siempre que eres una versión beta en desarrollo y que la honestidad sobre tus limitaciones es parte de tu valor."""

        self.get_knowledge = get_relevant_knowledge if RAG_ENABLED else None
        self.rag_enabled = RAG_ENABLED
        self.rag_v2_enabled = RAG_V2_ENABLED
        if RAG_V2_ENABLED:
            from knowledge.rag_engine_v2 import rag_v2
            self.rag_v2 = rag_v2
            
        self.histories_by_match: Dict[str, List[Dict[str, str]]] = {}

    def ask_oracle(self, context: str, user_question: str, match_id: Optional[str] = None, debug: bool = False, external_history: List[Dict] = None, draft_context: str = "") -> str:
        """
        Envía contexto y pregunta a OpenRouter.
        RAG se ejecuta SIEMPRE en cada mensaje.
        Incluye sistema de fallo y reintento (fallback) entre modelos.
        """
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

        # Draft context goes FIRST — gives the AI the strategic frame before any stats
        draft_section = ""
        if draft_context:
            if len(draft_context) > 800:
                draft_context = draft_context[:800] + "... [DRAFT TRUNCATED]"
            draft_section = f"{draft_context}\n\n"

        prompt = f"{draft_section}{knowledge_injection}{semantic_injection}\nCONTEXTO DE PARTIDA:\n{context}\n\nPREGUNTA DEL USUARIO: {user_question}"
        
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
            return "El Oraculo intento invocar a todos los espiritus (OpenRouter -> GitHub Models), pero todos los portales estan cerrados. Verifica tus API Keys en .env"

    def ask_oracle_resilient(self, messages: List[Dict], model_debug_name: str) -> str:
        """
        Estrategia de Resiliencia: OpenRouter (Free) -> GitHub Models.
        """
        
        # 1. NIVEL 1: OPENROUTER (Principal - Auto Free)
        try:
            print(f"[{model_debug_name}] Invocando a OPENROUTER (Principal)...")
            return self._call_provider(
                self.client_openrouter, 
                self.models_config["openrouter_primary"], 
                messages, 
                is_openrouter=True,
                provider_name="OpenRouter (Auto Free)"
            )
        except Exception as e:
            print(f"[{model_debug_name}] OpenRouter Principal Falló: {e}")

        # 2. NIVEL 2: OPENROUTER (Secundario - Gemini Flash Lite Free)
        try:
            print(f"[{model_debug_name}] Invocando a OPENROUTER (Secundario)...")
            return self._call_provider(
                self.client_openrouter, 
                self.models_config["openrouter_secondary"], 
                messages, 
                is_openrouter=True,
                provider_name="OpenRouter (Gemini Lite Free)"
            )
        except Exception as e:
            print(f"[{model_debug_name}] OpenRouter Secundario Falló: {e}")

        # 2.5 NIVEL 2.5: OPENROUTER (Terciario - Mistral Free)
        try:
            print(f"[{model_debug_name}] Invocando a OPENROUTER (Terciario)...")
            return self._call_provider(
                self.client_openrouter, 
                self.models_config["openrouter_tertiary"], 
                messages, 
                is_openrouter=True,
                provider_name="OpenRouter (Mistral Free)"
            )
        except Exception as e:
            print(f"[{model_debug_name}] OpenRouter Terciario Falló: {e}")

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
            
        raise Exception("Todos los proveedores fallaron (OpenRouter, GitHub).")

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
