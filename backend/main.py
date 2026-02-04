from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from services import opendota_service
from services import firebase_service
from services import tts_service
from services.ai_coach import oracle
from services.stratz_service import stratz
import os

# Load .env from project root
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path)

app = FastAPI(title="OracleDota Backend", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, we can tighten this to Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class ChatRequest(BaseModel):
    match_id: str
    query: str
    user_id: str

class ChatResponse(BaseModel):
    response: str

class ChatHistoryResponse(BaseModel):
    history: list

class TTSRequest(BaseModel):
    text: str

# --- ROUTES ---

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Generates audio for the given text using Edge TTS (Streaming)"""
    try:
        audio_bytes = await tts_service.generate_audio_stream(request.text)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        print(f"[TTS] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def quick_answer_router(data: dict, query: str) -> str | None:
    """
    Attempts to answer simple questions using raw data to save AI tokens.
    Returns None if the question requires AI analysis.
    """
    q = query.lower()
    
    # 1. Winner / Result
    if any(x in q for x in ["ganó", "gano", "ganador", "winner", "quien ganó"]):
        exclusion_terms = ["linea", "línea", "mid", "top", "bot", "fase", "lane", "minuto", "10", "vs", "duelo"]
        if not any(ex in q for ex in exclusion_terms):
            return f"Ganó {data['metadata']['winner']}."
    
    # 2. Duracion
    if any(x in q for x in ["duración", "duracion", "tiempo", "cuanto duró", "cuanto duro"]):
        return f"La partida duró {data['metadata']['duration_minutes']} minutos."

    # 3. Estadisticas del jugador
    stat_map = {
        "kda": "kda",
        "kills": "kda",
        "networth": "networth",
        "oro": "networth",
        "gold": "networth",
        "nivel": "level",
        "level": "level"
    }
    
    requested_stat = None
    target_key = None
    
    for keyword, key in stat_map.items():
        if keyword in q:
            requested_stat = keyword
            target_key = key
            break
            
    if target_key:
        for p in data['players']:
            if p['name'].lower() in q:
                val = p[target_key]
                if target_key == "kda":
                    return f"{p['name']} terminó con un KDA de {val}."
                elif target_key == "networth":
                    return f"{p['name']} tuvo un Networth de {val}."
                elif target_key == "level":
                    return f"{p['name']} alcanzó el nivel {val}."
                    
    return None

@app.get("/match/{match_id}")
async def get_match_details(match_id: str, background_tasks: BackgroundTasks):
    """Obtains detailed match metrics (Cached)"""
    # 1. Try Firestore
    try:
        data = firebase_service.get_match_from_db(match_id)
        if data:
            # If data is NOT partial, return it immediately
            if not data.get("metadata", {}).get("partial_data"):
                print(f"[CACHE] Match {match_id} found in DB (Full).")
                return data
            else:
                print(f"[CACHE] Match {match_id} in DB is PARTIAL. Attempting to refresh...")
    except Exception as e:
        print(f"[ERROR] DB lookup failed for match {match_id}: {e}")

    # 2. Try OpenDota
    try:
        print(f"[PROCESS] Processing match {match_id} from API...")
        match_data = opendota_service.get_match_data(match_id)
        
        if "error" in match_data:
            print(f"[ERROR] OpenDota API error for match {match_id}: {match_data['error']}")
            raise HTTPException(status_code=404, detail=match_data["error"])

        data = opendota_service.process_match_data(match_data)
        
        # 3. Save to DB (Synchronous for stability now)
        try:
            # Prevent overwriting FULL data with PARTIAL data
            existing = firebase_service.get_match_from_db(match_id)
            if not existing or (existing.get("metadata", {}).get("partial_data") and not data.get("metadata", {}).get("partial_data")):
                firebase_service.save_match_to_db(match_id, data)
                print(f"[DB] Match {match_id} saved/updated in DB.")
            else:
                print(f"[DB] Match {match_id} NOT updated (Existing data is more complete).")
        except Exception as e:
            print(f"[ERROR] Failed to save match {match_id} to DB: {e}")
            
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[FATAL ERROR] Match processing crashed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_oracle(request: ChatRequest, background_tasks: BackgroundTasks):
    """Chat with the AI Coach (Optimized)"""
    match_id = request.match_id
    query = request.query.strip()
    user_id = request.user_id
    
    # ASYNC: Save User Query to History (Legacy support, no blocking)
    background_tasks.add_task(firebase_service.save_chat_message, user_id, match_id, "user", query)
    
    # 1. Fetch Data (From DB or API)
    data = firebase_service.get_match_from_db(match_id)
    
    # Re-fetch if not in DB OR if DB data is partial
    if not data or data.get("metadata", {}).get("partial_data"):
        print(f"[FETCH] Match {match_id} missing or partial in DB. Fetching from OpenDota...")
        raw = opendota_service.get_match_data(match_id)
        if "error" in raw:
             if not data: # If no DB data at all, fail
                 raise HTTPException(status_code=404, detail=raw['error'])
             # If we have partial data and API fails, keep what we have
             print(f"[WARNING] API fetch failed during re-parse, keeping partial data: {raw['error']}")
        else:
            new_data = opendota_service.process_match_data(raw)
            # Update DB and Local pointer
            firebase_service.save_match_to_db(match_id, new_data)
            data = new_data
    
    # 2. Quick Answer Check
    quick_answer = quick_answer_router(data, query)
    if quick_answer:
        background_tasks.add_task(firebase_service.save_chat_message, user_id, match_id, "assistant", quick_answer)
        return ChatResponse(response=quick_answer)

    # 3. Get History for Context
    history = firebase_service.get_chat_history(user_id, match_id)
    
    # 4. Complexity Detection (Router)
    deep_keywords = [
        "analiza", "porque", "por qué", "detallado", "línea de tiempo", 
        "vision", "wards", "build", "itemizacion", "comparación",
        "pelea", "fight", "teamfight", "batalla", "conflicto",
        "poderes", "habilidad", "skills", "ultis", "daño", "damage",
        "healing", "curación", "torres", "tower", "estadísticas", "stats",
        "linea", "línea", "lane", "mid", "top", "bot", "minuto", "10", "fase"
    ]
    is_complex = any(k in query.lower() for k in deep_keywords)
    
    # 5. AI Call
    # Generate context from match data
    context_list = [opendota_service.generate_ai_context(data, deep_mode=is_complex)]
    
    # 5.5 Advanced Stratz Context (if complex and key exists)
    if is_complex and os.getenv("STRATZ_API_KEY"):
        stratz_data = stratz.get_match_laning_data(match_id)
        if stratz_data:
            context_list.append(stratz.format_stratz_context(stratz_data))
            
    context = "\n".join(context_list)
    
    # Call Oracle with history
    response = oracle.ask_oracle(context, query, match_id=match_id, external_history=history)
    
    # ASYNC: Save Assistant Response (Legacy support)
    background_tasks.add_task(firebase_service.save_chat_message, user_id, match_id, "assistant", response)
    
    return ChatResponse(response=response)

@app.get("/chat/history/{match_id}", response_model=ChatHistoryResponse)
async def get_match_history(match_id: str, user_id: str):
    """Retrieve chat history for a specific user and match"""
    history = firebase_service.get_chat_history(user_id, match_id)
    return ChatHistoryResponse(history=history)

@app.get("/health")
def health_check():
    from services.ai_coach import oracle
    db_status = "connected" if firebase_service.get_db() else "disconnected"
    return {
        "status": "healthy",
        "ai_ready": oracle.openrouter_client is not None,
        "database": db_status,
        "version": "1.1.0"
    }

@app.post("/analyze/{match_id}", response_model=ChatResponse)
async def analyze_match(match_id: str, user_id: str = "guest"): # Optional user_id for analysis
    """Full deep analysis (Persistent)"""
    
    # 1. Fetch Data
    data = firebase_service.get_match_from_db(match_id)
    if not data:
        raw = opendota_service.get_match_data(match_id)
        if "error" in raw:
             raise HTTPException(status_code=404, detail=raw['error'])
        data = opendota_service.process_match_data(raw)
        firebase_service.save_match_to_db(match_id, data)
        
    query = "Haz un análisis completo e inmortal de esta partida: MVP, errores de itemización, control de mapa y timings."
    
    # Save trigger query
    firebase_service.save_chat_message(user_id, match_id, "user", query)
    
    # AI Process
    context_list = [opendota_service.generate_ai_context(data, deep_mode=True)]
    
    # Add Stratz for full analysis
    if os.getenv("STRATZ_API_KEY"):
        stratz_data = stratz.get_match_laning_data(match_id)
        context_list.append(stratz.format_stratz_context(stratz_data))
        
    context = "\n".join(context_list)
    history = firebase_service.get_chat_history(user_id, match_id)
    answer = oracle.ask_oracle(context, query, match_id=match_id, external_history=history)
    
    # Save response
    firebase_service.save_chat_message(user_id, match_id, "assistant", answer)
    
    return ChatResponse(response=answer)

# --- PLAYER DATA ROUTES ---

@app.get("/player/{account_id}/info")
async def get_player_profile(account_id: str):
    """Obtiene la información básica del perfil del jugador desde OpenDota"""
    info = opendota_service.get_player_info(account_id)
    if "error" in info:
        raise HTTPException(status_code=404, detail=info["error"])
    return info

@app.get("/player/{account_id}/latest")
async def get_player_latest_matches(account_id: str):
    """Retorna las últimas 20 partidas del jugador usando su Account ID"""
    matches = opendota_service.get_recent_matches(account_id)
    
    if isinstance(matches, dict) and "error" in matches:
        raise HTTPException(status_code=400, detail=matches["error"])
        
    return {
        "account_id": account_id,
        "count": len(matches),
        "matches": matches
    }

@app.post("/player/{account_id}/refresh")
async def refresh_player(account_id: str):
    """Solicita a OpenDota que actualice los datos del jugador"""
    result = opendota_service.refresh_player_data(account_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
