"""
Question Limit Service - Daily Limit System
Handles daily question quotas for free users (20/day) and donors (20/day).
"""

from datetime import datetime, timedelta, timezone
from firebase_admin import firestore

# Quotas
FREE_DAILY_LIMIT = 20
DONOR_DAILY_LIMIT = 20

def check_question_limit(user_id: str, db) -> dict:
    """
    Checks if a user can ask a question today.
    Returns: {
        "can_ask": bool,
        "remaining": int,
        "limit": int,
        "questions_used": int,
        "reset_in_hours": float,
        "is_donor": bool
    }
    """
    try:
        if not db:
            return {"can_ask": True, "limit": 999, "remaining": 999} # Fallback if DB fails
            
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            # New user, allow but track (init handled in first increment)
            return {
                "can_ask": True, 
                "remaining": FREE_DAILY_LIMIT, 
                "limit": FREE_DAILY_LIMIT,
                "questions_used": 0,
                "is_donor": False
            }
        
        user_data = user_doc.to_dict()
        is_donor = user_data.get("is_donor", False)
        daily_limit = DONOR_DAILY_LIMIT if is_donor else FREE_DAILY_LIMIT
        
        questions_used = user_data.get("questions_used_today", 0)
        last_question_date = user_data.get("last_question_date")
        
        # Check if reset is needed (new day)
        now = datetime.now(timezone.utc)
        today = now.date()
        needs_reset = False
        
        if not last_question_date:
            needs_reset = True
        else:
            # Firestore puede devolver DatetimeWithNanoseconds (subclase de datetime),
            # datetime naive (Python), o en raros casos un string ISO.
            # Normalizamos todo a una fecha UTC comparable.
            try:
                if isinstance(last_question_date, datetime):
                    # Puede ser timezone-aware (Firestore) o naive (Python)
                    if last_question_date.tzinfo is not None:
                        last_date = last_question_date.astimezone(timezone.utc).date()
                    else:
                        last_date = last_question_date.date()
                elif isinstance(last_question_date, str):
                    # Fallback para strings ISO almacenados manualmente
                    parsed = datetime.fromisoformat(last_question_date.replace('Z', '+00:00'))
                    last_date = parsed.date()
                else:
                    # Tipo desconocido: intentar convertir como Firestore Timestamp
                    last_date = last_question_date.date()
                    
                if last_date < today:
                    needs_reset = True
            except Exception as ts_err:
                print(f"[QUESTION_LIMIT] Warning: No se pudo parsear last_question_date ({type(last_question_date)}): {ts_err}. Permitiendo pregunta sin resetear.")
                # En caso de error, NO forzamos reset para no romper el límite.
                needs_reset = False
        
        if needs_reset:
            user_ref.update({
                "questions_used_today": 0,
                "last_question_date": now
            })
            questions_used = 0
            
        remaining = max(0, daily_limit - questions_used)
        can_ask = questions_used < daily_limit
        
        # Calculate reset time (midnight)
        tomorrow = datetime.combine(today + timedelta(days=1), datetime.min.time())
        hours_until_reset = (tomorrow - now).total_seconds() / 3600
        
        return {
            "can_ask": can_ask,
            "remaining": remaining,
            "limit": daily_limit,
            "questions_used": questions_used,
            "reset_in_hours": round(hours_until_reset, 1),
            "is_donor": is_donor
        }
        
    except Exception as e:
        print(f"[QUESTION_LIMIT] Error: {e}")
        return {"can_ask": True, "error": str(e)}

def increment_question_count(user_id: str, db):
    """Increments the daily question counter for a user"""
    try:
        if not db: return
        
        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "questions_used_today": firestore.Increment(1),
            "last_question_date": datetime.now(timezone.utc)  # Siempre UTC para consistencia
        })
        print(f"[QUESTION_LIMIT] Incremented count for {user_id}")
    except Exception as e:
        print(f"[QUESTION_LIMIT] Error incrementing: {e}")
