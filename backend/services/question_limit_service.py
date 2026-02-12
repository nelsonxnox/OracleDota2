"""
Question Limit Service - Daily Limit System with Donor Tier
- Free users: 3 preguntas/día
- Donors: 20 preguntas/día (cualquier donación)
"""

from datetime import datetime, timedelta
from firebase_admin import firestore

# Límites diarios por tier
DAILY_LIMITS = {
    "free": 3,
    "donor": 20
}

def check_question_limit(user_id: str, db) -> dict:
    """
    Verifica si el usuario puede hacer una pregunta hoy
    Returns: {
        "can_ask": bool,
        "remaining": int,
        "limit": int,
        "questions_used": int,
        "tier": str,  # "free" o "donor"
        "reset_in_hours": float
    }
    """
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return {"can_ask": False, "error": "User not found"}
        
        user_data = user_doc.to_dict()
        
        # Determinar tier del usuario
        is_donor = user_data.get("is_donor", False)
        tier = "donor" if is_donor else "free"
        
        questions_used = user_data.get("questions_used_today", 0)
        last_question_date = user_data.get("last_question_date")
        
        # Verificar si necesita reset (nuevo día)
        now = datetime.now()
        today = now.date()
        needs_reset = False
        
        if not last_question_date:
            needs_reset = True
        elif isinstance(last_question_date, datetime):
            if last_question_date.date() < today:
                needs_reset = True
        
        if needs_reset:
            # Reset contador diario
            user_ref.update({
                "questions_used_today": 0,
                "last_question_date": now
            })
            questions_used = 0
        
        # Obtener límite según tier
        limit = DAILY_LIMITS.get(tier, 3)
        
        remaining = max(0, limit - questions_used)
        can_ask = questions_used < limit
        
        # Calcular hora del próximo reset (medianoche)
        tomorrow = datetime.combine(today + timedelta(days=1), datetime.min.time())
        hours_until_reset = (tomorrow - now).total_seconds() / 3600
        
        return {
            "can_ask": can_ask,
            "remaining": remaining,
            "limit": limit,
            "questions_used": questions_used,
            "tier": tier,
            "reset_in_hours": round(hours_until_reset, 1)
        }
    except Exception as e:
        print(f"[QUESTION_LIMIT] Error checking limit: {e}")
        return {"can_ask": False, "error": str(e)}

def increment_question_count(user_id: str, db):
    """Incrementa el contador de preguntas del usuario"""
    try:
        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "questions_used_today": firestore.Increment(1),
            "last_question_date": datetime.now()
        })
        print(f"[QUESTION_LIMIT] Incremented daily question count for user {user_id}")
    except Exception as e:
        print(f"[QUESTION_LIMIT] Error incrementing count: {e}")

def upgrade_to_donor(user_id: str, db, donation_amount: float = 0):
    """
    Actualiza un usuario a tier 'donor' después de una donación
    
    Args:
        user_id: ID del usuario
        db: Firestore database instance
        donation_amount: Monto de la donación (opcional, para tracking)
    """
    try:
        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "is_donor": True,
            "donor_since": datetime.now(),
            "total_donated": firestore.Increment(donation_amount)
        })
        print(f"[QUESTION_LIMIT] Upgraded user {user_id} to donor tier (${donation_amount})")
        return True
    except Exception as e:
        print(f"[QUESTION_LIMIT] Error upgrading user to donor: {e}")
        return False

def get_tier_info(tier: str) -> dict:
    """Retorna información sobre un tier específico"""
    tiers = {
        "free": {
            "name": "Gratuito",
            "questions_per_day": 3,
            "features": [
                "3 preguntas diarias al AI Coach",
                "Análisis básico de partidas",
                "Acceso a estadísticas"
            ]
        },
        "donor": {
            "name": "Donador",
            "questions_per_day": 20,
            "features": [
                "20 preguntas diarias al AI Coach",
                "Análisis avanzado de partidas",
                "Acceso prioritario a nuevas features",
                "Agradecimiento en la página de donadores"
            ]
        }
    }
    return tiers.get(tier, tiers["free"])
