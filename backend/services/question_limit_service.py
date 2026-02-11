"""
Question Limit Service
Manages question limits for different user plans
"""

from datetime import datetime, timedelta
from firebase_admin import firestore

QUESTION_LIMITS = {
    "free": 3,
    "basic": float('inf'),  # Unlimited
    "premium": float('inf')  # Unlimited
}

def check_question_limit(user_id: str, db) -> dict:
    """
    Verifica si el usuario puede hacer una pregunta
    Returns: {
        "can_ask": bool,
        "remaining": int | float,
        "plan_type": str,
        "limit": int | float,
        "questions_used": int
    }
    """
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return {"can_ask": False, "error": "User not found"}
        
        user_data = user_doc.to_dict()
        plan_type = user_data.get("plan_type", "free")
        questions_used = user_data.get("questions_used_this_month", 0)
        reset_date = user_data.get("questions_reset_date")
        
        # Verificar si necesita reset (nuevo mes)
        now = datetime.now()
        needs_reset = False
        
        if not reset_date:
            needs_reset = True
        elif isinstance(reset_date, datetime):
            if reset_date < now:
                needs_reset = True
        
        if needs_reset:
            # Reset contador
            next_month = now + timedelta(days=30)
            user_ref.update({
                "questions_used_this_month": 0,
                "questions_reset_date": next_month
            })
            questions_used = 0
        
        limit = QUESTION_LIMITS.get(plan_type, 3)
        
        if limit == float('inf'):
            remaining = float('inf')
            can_ask = True
        else:
            remaining = max(0, limit - questions_used)
            can_ask = questions_used < limit
        
        return {
            "can_ask": can_ask,
            "remaining": remaining,
            "plan_type": plan_type,
            "limit": limit,
            "questions_used": questions_used
        }
    except Exception as e:
        print(f"[QUESTION_LIMIT] Error checking limit: {e}")
        return {"can_ask": False, "error": str(e)}

def increment_question_count(user_id: str, db):
    """Incrementa el contador de preguntas del usuario"""
    try:
        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "questions_used_this_month": firestore.Increment(1)
        })
        print(f"[QUESTION_LIMIT] Incremented question count for user {user_id}")
    except Exception as e:
        print(f"[QUESTION_LIMIT] Error incrementing count: {e}")

def get_plan_info(plan_type: str) -> dict:
    """Retorna información sobre un plan específico"""
    plans = {
        "free": {
            "name": "Gratuito",
            "price": 0,
            "questions_per_month": 3,
            "live_tokens": 1,
            "features": [
                "1 token de coaching en vivo",
                "3 preguntas al mes",
                "Análisis básico de partidas"
            ]
        },
        "basic": {
            "name": "Básico",
            "price": 1.99,
            "questions_per_month": "ilimitadas",
            "live_tokens": 10,
            "features": [
                "10 tokens de coaching",
                "Preguntas ilimitadas",
                "Análisis avanzado",
                "Soporte prioritario"
            ]
        },
        "premium": {
            "name": "Premium",
            "price": 2.50,
            "questions_per_month": "ilimitadas",
            "live_tokens": 50,
            "features": [
                "50 tokens de coaching",
                "Preguntas ilimitadas",
                "Análisis profundo con IA",
                "Soporte VIP 24/7"
            ]
        }
    }
    return plans.get(plan_type, plans["free"])
