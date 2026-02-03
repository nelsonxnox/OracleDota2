from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import opendota_service
import firebase_service
from ai_coach import oracle
import os

load_dotenv()

app = FastAPI(title="OracleDota Backend", version="1.1.0")

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

# --- ROUTES ---

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
async def get_match_details(match_id: str):
    """Fetch and parse a match (DB -> OpenDota -> DB)"""
    
    # 1. Try DB
    db_data = firebase_service.get_match_from_db(match_id)
    if db_data:
        return db_data
    
    # 2. Try OpenDota
    print(f"[PROCESS] Processing match {match_id} from API...")
    match_data = opendota_service.get_match_data(match_id)
    
    if "error" in match_data:
        raise HTTPException(status_code=404, detail=match_data["error"])

    processed_data = opendota_service.process_match_data(match_data)
    
    # 3. Save to DB
    firebase_service.save_match_to_db(match_id, processed_data)
    
    return processed_data

@app.post("/chat", response_model=ChatResponse)
async def chat_with_oracle(request: ChatRequest):
    """Chat with the AI Coach (Persistent history per User)"""
    match_id = request.match_id
    query = request.query.strip()
    user_id = request.user_id
    
    # Save User Query to History immediately
    firebase_service.save_chat_message(user_id, match_id, "user", query)
    
    # 1. Fetch Data (DB or API)
    data = firebase_service.get_match_from_db(match_id)
    if not data:
        # Fallback if chat called before match view (rare)
        raw = opendota_service.get_match_data(match_id)
        if "error" in raw:
             raise HTTPException(status_code=404, detail=raw['error'])
        data = opendota_service.process_match_data(raw)
        firebase_service.save_match_to_db(match_id, data)
    
    # 2. Quick Answer Check (Save tokens)
    quick_answer = quick_answer_router(data, query)
    if quick_answer:
        firebase_service.save_chat_message(user_id, match_id, "assistant", quick_answer)
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
    context = opendota_service.generate_ai_context(data, deep_mode=is_complex)
    
    # We pass the history explicitly now
    answer = oracle.ask_oracle(context, query, match_id=match_id, external_history=history)
    
    # 6. Save Response
    firebase_service.save_chat_message(user_id, match_id, "assistant", answer)
    
    return ChatResponse(response=answer)

@app.get("/chat/history/{match_id}", response_model=ChatHistoryResponse)
async def get_match_history(match_id: str, user_id: str):
    """Retrieve chat history for a specific user and match"""
    history = firebase_service.get_chat_history(user_id, match_id)
    return ChatHistoryResponse(history=history)

@app.get("/health")
def health_check():
    from ai_coach import oracle
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
    context = opendota_service.generate_ai_context(data, deep_mode=True)
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
