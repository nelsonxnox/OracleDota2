"""
Question Limit Service - Daily Limit System
Handles daily question quotas for free users (3/day) and donors (20/day).
"""

from datetime import datetime, timedelta
from firebase_admin import firestore

# Quotas
FREE_DAILY_LIMIT = 30
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
        now = datetime.now()
        today = now.date()
        needs_reset = False
        
        if not last_question_date:
            needs_reset = True
        else:
            # Handle different timestamp formats from Firebase
            if isinstance(last_question_date, datetime):
                last_date = last_question_date.date()
            else:
                # Fallback for strings or other types if necessary
                needs_reset = True
                last_date = None
                
            if last_date and last_date < today:
                needs_reset = True
        
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
            "last_question_date": datetime.now()
        })
        print(f"[QUESTION_LIMIT] Incremented count for {user_id}")
    except Exception as e:
        print(f"[QUESTION_LIMIT] Error incrementing: {e}")
