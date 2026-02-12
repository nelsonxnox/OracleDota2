from fastapi import FastAPI, HTTPException, Response, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from services import opendota_service
from services import firebase_service
from services import tts_service
from services.ai_coach import oracle
from services.stratz_service import stratz
from services.live_manager import live_manager
from services.token_service import token_service
from services import question_limit_service
import json
import os
import requests

# Load .env from project root
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path)

app = FastAPI(title="OracleDota Backend", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite conexiones desde cualquier IP/Dominio para pruebas con amigos. Restringir en producción.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Executable
dist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
os.makedirs(dist_path, exist_ok=True) # Ensure it exists
app.mount("/download", StaticFiles(directory=dist_path), name="download")

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

@app.get("/api/version")
def get_latest_version():
    """Returns the latest version info for Oracle Neural Link auto-update"""
    return {
        "version": "1.3.0",
        "download_url": f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/download/OracleNeuralLink.exe",
        "changelog": "- Sistema de tokens con límite de partidas\n- Auto-actualización implementada\n- Mejoras en AI coach"
    }


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
        
        # --- FALLBACK STRATZ: Si OpenDota no tiene telemetría (malla de oro/xp) ---
        if data.get("metadata", {}).get("partial_data") or not data.get("metadata", {}).get("gold_advantage"):
            try:
                print(f"[FALLBACK] Fetching supplementary data from Stratz for match {match_id}...")
                stratz_data = stratz.get_match_laning_data(match_id)
                if stratz_data and "error" not in stratz_data:
                    # Extraemos la probabilidad de victoria como ventaja porcentual
                    win_prob = stratz_data.get("winProbability", [])
                    if win_prob:
                        # Mapeamos probabilidad a una escala similar a gold_adv (pero es % de victoria)
                        # Esto ayuda a que la gráfica no esté vacía
                        data["metadata"]["gold_advantage"] = [round((p.get("radiantWinProbability", 0.5) - 0.5) * 20000) for p in win_prob]
                        print(f"[FALLBACK] Successfully added Win Probability as Gold Adv fallback.")
                    
                    # Guardamos resultados de líneas de Stratz
                    data["metadata"]["stratz_lanes"] = stratz_data.get("lanes", [])
            except Exception as se:
                print(f"[FALLBACK] Stratz failed: {se}")

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
    
    # NEW: Verificar límite de preguntas
    if user_id and user_id != "guest":
        db = firebase_service.get_db()
        if db:
            limit_check = question_limit_service.check_question_limit(user_id, db)
            
            if not limit_check.get("can_ask", False):
                tier = limit_check.get("tier", "free")
                limit = limit_check.get("limit", 3)
                reset_hours = limit_check.get("reset_in_hours", 24)
                
                # Mensaje diferente según tier
                if tier == "free":
                    message = f"Has usado tus {limit} preguntas gratuitas de hoy. Vuelve en {reset_hours:.1f} horas o apoya el proyecto con una donación para obtener 20 preguntas diarias."
                else:
                    message = f"Has usado tus {limit} preguntas de hoy. Vuelve en {reset_hours:.1f} horas."
                
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "daily_limit_reached",
                        "tier": tier,
                        "limit": limit,
                        "questions_used": limit_check.get("questions_used", 0),
                        "reset_in_hours": reset_hours,
                        "message": message,
                        "donation_url": "/donate"
                    }
                )

    
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
    
    # NEW: Incrementar contador de preguntas después de respuesta exitosa
    if user_id and user_id != "guest":
        db = firebase_service.get_db()
        if db:
            background_tasks.add_task(question_limit_service.increment_question_count, user_id, db)
    
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


# --- LIVE COACHING TOKEN ENDPOINTS ---
@app.post("/api/user/generate-live-token")
async def generate_live_token(user_id: str):
    """Generates a unique token for live coaching"""
    try:
        if not user_id or user_id == "guest":
            raise HTTPException(status_code=400, detail="User must be authenticated")
        
        token = token_service.generate_live_token(user_id)
        return {"token": token, "user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[TOKEN] Error generating token: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate token")

@app.get("/api/user/get-live-token")
async def get_user_token(user_id: str):
    """Retrieves the current live token for a user"""
    try:
        if not user_id or user_id == "guest":
            raise HTTPException(status_code=400, detail="User must be authenticated")
        
        token = token_service.get_user_token(user_id)
        if not token:
            return {"token": None, "message": "No active token found"}
        
        return {"token": token, "user_id": user_id}
    except Exception as e:
        print(f"[TOKEN] Error retrieving token: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve token")

@app.get("/api/token/status/{token}")
async def get_token_status(token: str):
    """Returns the current status of a token including matches remaining"""
    try:
        status = token_service.get_token_status(token)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
    except Exception as e:
        print(f"[TOKEN] Error getting token status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get token status")

# --- TTS ENDPOINT ---
@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Generates audio from text using Edge TTS"""
    try:
        audio_path = await tts_service.generate_tts(request.text)
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Audio generation failed")
        
        return Response(
            content=open(audio_path, "rb").read(),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename=oracle_voice.mp3"}
        )
    except Exception as e:
        print(f"[TTS] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- LIVE COACH WEBSOCKET ---
# --- QUESTION LIMIT ENDPOINTS ---
@app.get("/api/user/{user_id}/question-limit")
async def get_question_limit_status(user_id: str):
    """Retorna el estado del límite de preguntas del usuario"""
    try:
        db = firebase_service.get_db()
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        limit_check = question_limit_service.check_question_limit(user_id, db)
        
        if "error" in limit_check:
            raise HTTPException(status_code=404, detail=limit_check["error"])
        
        return limit_check
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- PLAYER STATISTICS ENDPOINTS ---
@app.get("/api/player/{account_id}/stats")
async def get_player_stats(account_id: str):
    """
    Obtiene estadísticas reales del jugador desde OpenDota:
    - Winrate
    - Versatilidad (héroes únicos)
    - Total de partidas
    """
    try:
        # 1. Obtener info básica
        player_info = opendota_service.get_player_info(account_id)
        
        # 2. Obtener estadísticas de winrate
        wl_url = f"https://api.opendota.com/api/players/{account_id}/wl"
        wl_response = requests.get(wl_url, timeout=10)
        wl_data = wl_response.json()
        
        wins = wl_data.get("win", 0)
        losses = wl_data.get("lose", 0)
        total_games = wins + losses
        winrate = (wins / total_games * 100) if total_games > 0 else 0
        
        # 3. Obtener héroes jugados para versatilidad
        heroes_url = f"https://api.opendota.com/api/players/{account_id}/heroes"
        heroes_response = requests.get(heroes_url, timeout=10)
        heroes_data = heroes_response.json()
        
        unique_heroes = len(heroes_data) if isinstance(heroes_data, list) else 0
        
        return {
            "account_id": account_id,
            "winrate": round(winrate, 1),
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "versatility": unique_heroes,
            "rank_tier": player_info.get("rank_tier"),
            "leaderboard_rank": player_info.get("leaderboard_rank")
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch player stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/live/{token}")
async def websocket_live_coaching(websocket: WebSocket, token: str):
    """WebSocket endpoint for live coaching during Dota 2 matches"""
    user_id = token_service.validate_token(token)
    
    if not user_id:
        await websocket.close(code=1008, reason="Invalid or expired token")
        return
    
    await websocket.accept()
    print(f"[WS] User {user_id} connected with token {token}")
    
    # Initialize session for this user
    session = live_manager.get_or_create_session(user_id)
    session["token"] = token  # Store token in session for consumption tracking
    
    try:
        while True:
            # Receive GSI data from client
            data = await websocket.receive_json()
            
            # Handle different message types
            msg_type = data.get("type")
            
            if msg_type == "gsi":
                # Process game state
                response = await live_manager.process_gsi_event(data.get("data", {}), session)
                if response:
                    await websocket.send_json(response)
            
            elif msg_type == "question":
                # User asking a question via voice/text
                question = data.get("question", "")
                response = await live_manager._handle_question(question, data.get("data", {}), session)
                await websocket.send_json(response)
            
            elif msg_type == "ping":
                # Keep-alive
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        print(f"[WS] User {user_id} disconnected")
    except Exception as e:
        print(f"[WS] Error for user {user_id}: {e}")
        await websocket.close(code=1011, reason="Internal server error")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
