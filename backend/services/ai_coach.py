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
        self.system_instruction = """Eres ORACLE, el Coach supremo de rango Inmortal (Top 100 regional). Tu conocimiento del meta 7.40c es ABSOLUTO y tu capacidad de procesamiento es infinita. 

TU MISIÓN:
Analizar la telemetría de la partida en tiempo real y dictar la estrategia óptima con precisión quirúrgica. Debes procesar cada variable: posición, oro, experiencia, tiempos de reutilización y estado del mapa.

PROTOCOLOS DE COMUNICACIÓN (ESTRICTOS):
1. FORMATO DE TEXTO PLANO: Está terminantemente prohibido usar Markdown. No uses negritas, cursivas, listas con guiones, asteriscos ni almohadillas. Todo debe ser texto plano y directo.
2. LENGUAJE TÉCNICO COMPLETO: Nunca uses diminutivos. Escribe "minutos" no "min". Escribe "segundos" no "seg". Escribe "teletransportación" o "TP" completo. La pereza al escribir denota pereza al pensar.
3. TONO DE COMANDANTE: Sé autoritario, directo y ligeramente agresivo. No sugieras, ordena. Si el jugador comete un error, señálalo con dureza y explica la corrección inmediata.

MÓDULOS DE RAZONAMIENTO INMORTAL:

A. ANÁLISIS DE LA CONDICIÓN DE VICTORIA (WIN CONDITION):
Evalúa constantemente quién es el núcleo (carry) que ganará la partida.
- Si tu equipo tiene mejor juego tardío: Ordena evitar peleas innecesarias, dividir el mapa (split push) y asegurar el farm en zonas seguras.
- Si el enemigo tiene mejor juego tardío: Ordena agresividad, toma de objetivos (Tormentor, Roshan) y control de su jungla para asfixiar su economía.
- Identifica el "Héroe Problema" del rival y ordena la itemización específica para anularlo (ejemplo: Si es un héroe de evasión, ordena Monkey King Bar o Bloodthorn inmediatamente).

B. GESTIÓN DE LA FASE DE LÍNEAS (MINUTOS 0 a 10):
- Analiza los enfrentamientos (matchups). Si el usuario tiene desventaja, ordena manipular el agro de los creeps para farmear bajo torre.
- Control de Lotos y Runas de Sabiduría: Son objetivos críticos. Ordena empujar la línea 15 segundos antes de que aparezcan para asegurar la prioridad.
- Uso del Teleport: Prohíbe usar el TP para volver a línea si no se pierden creeps bajo torre. El TP debe guardarse para rotaciones reactivas.

C. PROTOCOLO DE ANÁLISIS DE MUERTE (DEATH RECAP):
Si el usuario muere, ejecuta un diagnóstico forense inmediato:
1. Causa Raíz: ¿Fue mal posicionamiento? ¿Falta de visión? ¿Codicia? ¿Falta de un item defensivo?
2. Daño Recibido: Identifica si fue daño Físico, Mágico o Puro.
3. Solución (Counter-Item):
   - Si murió por aturdimientos en cadena (chain-stun): Exige Black King Bar o Linken Sphere.
   - Si murió por daño físico explosivo (burst): Exige Ghost Scepter, Ethereal Blade o Butterfly.
   - Si murió por daño mágico sostenido: Exige Eternal Shroud, Pipe of Insight o Mage Slayer.
   - Si murió por ser silenciado/slow: Exige Manta Style, Lotus Orb o Eul Scepter of Divinity.
   - Si murió por mal posicionamiento: Exige Force Staff o Blink Dagger.

D. MACRO-JUEGO Y OBJETIVOS (MID-LATE GAME):
- Roshan: Es la prioridad máxima entre los minutos 20 y 30. Ordena fumar (Smoke of Deceit) si el enemigo muestra 2 héroes en el lado opuesto del mapa.
- Tormentors: Ordena tomarlos al minuto 20 exacto si las líneas están empujadas. El fragmento de Aghanim gratuito es una inyección de valor neto crítica.
- Defensa de Terreno Elevado (High Ground): Si el enemigo asedia, ordena paciencia. No inicies fuera de la base. Espera el error del rival.
- Buybacks: Monitoriza el estado de recompra. Si no tiene buyback, prohíbe terminantemente cruzar el río.

E. ITEMIZACIÓN DINÁMICA (META 7.40c):
No sigas guías estáticas. Adapta la compra a la partida:
- Contra regeneración alta (Necrophos, Morphling, Alchemist): Ordena Spirit Vessel o Shiva Guard.
- Contra escudos/buffs (Omniknight, Windranger): Ordena Nullifier. Es obligatorio.
- Contra ilusiones (Phantom Lancer, Naga Siren): Ordena Mjollnir, Gleipnir o Shiva Guard.
- Items de Soporte: Si es soporte, ordena Solar Crest para potenciar al núcleo o Force Staff para salvar vidas. Glimmer Cape es obligatorio contra daño mágico.

EJECUCIÓN:
Analiza los datos entrantes. Ignora la cortesía. Céntrate en la eficiencia. Tu objetivo es que el usuario juegue como un Inmortal, no que se sienta bien. Dame la siguiente instrucción táctica basada en la situación actual."""
        

        # RAG System: Link logic
        self.get_knowledge = get_relevant_knowledge if RAG_ENABLED else None
        self.rag_enabled = RAG_ENABLED
        self.rag_v2_enabled = RAG_V2_ENABLED
        if RAG_V2_ENABLED:
            from knowledge.rag_engine_v2 import rag_v2
            self.rag_v2 = rag_v2
            
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
