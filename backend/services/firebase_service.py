import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

# Singleton DB instance
db = None

def get_db():
    global db
    if db is None:
        # Check for credentials in Env Var (JSON content) - Best for Cloud (Render/Vercel)
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        cred_path = os.getenv("FIREBASE_CREDENTIALS")
        
        try:
            if cred_json:
                print("[FIREBASE] Initializing with CREDENTIALS_JSON env var...")
                import json
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            elif cred_path and os.path.exists(cred_path):
                print(f"[FIREBASE] Initializing with credentials from {cred_path}")
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Try default credentials (gcloud auth application-default login)
                print("[FIREBASE] Initializing with Default Credentials...")
                firebase_admin.initialize_app()
            
            db = firestore.client()
            print("[FIREBASE] Firestore connected successfully.")
        except ValueError:
             # Already initialized
             db = firestore.client()
        except Exception as e:
            print(f"[FIREBASE] Error connecting: {e}")
            db = None
    return db

def save_match_to_db(match_id: str, data: dict):
    """Saves match analysis data to Firestore"""
    database = get_db()
    if not database: return
    
    try:
        # We store match data in a 'matches' collection
        doc_ref = database.collection("matches").document(str(match_id))
        doc_ref.set({
            "data": data,
            "updated_at": datetime.now()
        })
        print(f"[DB] Match {match_id} saved.")
    except Exception as e:
        print(f"[DB] Error saving match {match_id}: {e}")

def get_match_from_db(match_id: str) -> dict | None:
    """Retrieves match analysis data from Firestore"""
    database = get_db()
    if not database: return None
    
    try:
        doc_ref = database.collection("matches").document(str(match_id))
        doc = doc_ref.get()
        if doc.exists:
            print(f"[DB] Cache Hit for match {match_id}")
            return doc.to_dict().get("data")
    except Exception as e:
        print(f"[DB] Error retrieving match {match_id}: {e}")
    return None

def save_chat_message(user_id: str, match_id: str, role: str, content: str):
    """Saves a chat message to the user's history for a specific match"""
    database = get_db()
    if not database: return
    
    try:
        # Path: users/{user_id}/chats/{match_id}/messages/{auto_id}
        # This structure allows querying all chats for a user, or specific match chat
        
        # Ensure user document exists (optional, but good for indexing)
        user_ref = database.collection("users").document(user_id)
        # We don't overwrite user data here, just ensure path is valid conceptually
        
        messages_ref = user_ref.collection("chats").document(match_id).collection("messages")
        
        msg_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        }
        
        messages_ref.add(msg_data)
        
        # Update metadata for the chat (last message time)
        user_ref.collection("chats").document(match_id).set({
            "last_updated": datetime.now(),
            "match_id": match_id
        }, merge=True)
        
    except Exception as e:
        print(f"[DB] Error saving chat message: {e}")

def get_chat_history(user_id: str, match_id: str, limit: int = 50) -> list:
    """Retrieves chat history for a user and match"""
    database = get_db()
    if not database: return []
    
    try:
        messages_ref = database.collection("users").document(user_id)\
                               .collection("chats").document(match_id)\
                               .collection("messages")
        
        # Order by timestamp
        query = messages_ref.order_by("timestamp").limit(limit)
        docs = query.stream()
        
        history = []
        for doc in docs:
            d = doc.to_dict()
            history.append({
                "role": d.get("role"),
                "content": d.get("content")
            })
            
        return history
    except Exception as e:
        print(f"[DB] Error retrieving history: {e}")
        return []
