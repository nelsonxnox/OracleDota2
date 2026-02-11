import uuid
from datetime import datetime
from services.firebase_service import get_db

class TokenService:
    """Manages live coaching tokens for user authentication"""
    
    def generate_live_token(self, user_id: str, matches: int = 1, plan_type: str = "free") -> str:
        """
        Generates a unique token for a user's live coaching session.
        Always creates a new token and invalidates the previous one if it exists.
        
        Args:
            user_id: Firebase user ID
            matches: Number of matches this token is valid for (default: 1)
            plan_type: "free", "basic", or "premium"
        """
        if not user_id or user_id == "guest":
            raise ValueError("Guest users cannot use live coaching")
        
        db = get_db()
        if not db:
            raise Exception("No se pudo conectar a la base de datos de Firebase")
        
        # Check if user already has a token
        old_token = self.get_user_token(user_id)
        if old_token:
            print(f"[TOKEN] User {user_id} already has token {old_token}, revoking it and generating new one")
            self.revoke_token(old_token)
        
        # Generate new token
        token = str(uuid.uuid4())
        
        # Store in Firestore
        try:
            from firebase_admin import firestore
            
            token_ref = db.collection("live_tokens").document(token)
            token_ref.set({
                "user_id": user_id,
                "created_at": firestore.SERVER_TIMESTAMP,
                "active": True,
                "matches_remaining": matches,
                "plan_type": plan_type,
                "total_matches": matches,
                "last_match_id": None
            })
            
            # Also store reference in user doc for easy lookup
            user_ref = db.collection("users").document(user_id)
            user_ref.set({"live_token": token}, merge=True)
            
            print(f"[TOKEN] Generated new token {token} for user {user_id} with {matches} matches ({plan_type})")
            return token
        except Exception as e:
            print(f"[TOKEN] Error generating token: {e}")
            raise
    
    def get_user_token(self, user_id: str) -> str | None:
        """Retrieves existing token for a user"""
        try:
            db = get_db()
            if not db: return None
            
            user_ref = db.collection("users").document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                data = user_doc.to_dict()
                return data.get("live_token")
            return None
        except Exception as e:
            print(f"[TOKEN] Error retrieving token: {e}")
            return None
    
    def validate_token(self, token: str) -> str | None:
        """
        Validates a token and returns the associated user_id.
        Returns None if token is invalid or has no matches remaining.
        """
        try:
            db = get_db()
            if not db: return None

            token_ref = db.collection("live_tokens").document(token)
            token_doc = token_ref.get()
            
            if not token_doc.exists:
                print(f"[TOKEN] Invalid token: {token}")
                return None
            
            data = token_doc.to_dict()
            if not data.get("active", False):
                print(f"[TOKEN] Inactive token: {token}")
                return None
            
            # Check if token has matches remaining
            matches_remaining = data.get("matches_remaining", 0)
            if matches_remaining <= 0:
                print(f"[TOKEN] Token {token} has no matches remaining")
                self.revoke_token(token)
                return None
            
            user_id = data.get("user_id")
            print(f"[TOKEN] Valid token for user: {user_id} ({matches_remaining} matches remaining)")
            return user_id
        except Exception as e:
            print(f"[TOKEN] Error validating token: {e}")
            return None
    
    def consume_match(self, token: str, match_id: str = None) -> dict:
        """
        Consumes one match from the token.
        Returns dict with status and remaining matches.
        """
        try:
            db = get_db()
            if not db:
                return {"success": False, "error": "Database connection failed"}
            
            token_ref = db.collection("live_tokens").document(token)
            token_doc = token_ref.get()
            
            if not token_doc.exists:
                return {"success": False, "error": "Token not found"}
            
            data = token_doc.to_dict()
            
            # Prevent consuming the same match twice
            if match_id and data.get("last_match_id") == match_id:
                return {
                    "success": False, 
                    "error": "Match already consumed",
                    "matches_remaining": data.get("matches_remaining", 0)
                }
            
            matches_remaining = data.get("matches_remaining", 0)
            
            if matches_remaining <= 0:
                self.revoke_token(token)
                return {"success": False, "error": "No matches remaining"}
            
            new_remaining = matches_remaining - 1
            
            # Update token
            update_data = {
                "matches_remaining": new_remaining,
                "last_match_id": match_id
            }
            
            # Deactivate if no matches left
            if new_remaining <= 0:
                update_data["active"] = False
            
            token_ref.update(update_data)
            
            print(f"[TOKEN] Consumed 1 match from {token}. Remaining: {new_remaining}")
            
            return {
                "success": True,
                "matches_remaining": new_remaining,
                "plan_type": data.get("plan_type", "free")
            }
        except Exception as e:
            print(f"[TOKEN] Error consuming match: {e}")
            return {"success": False, "error": str(e)}
    
    def get_token_status(self, token: str) -> dict:
        """Returns the current status of a token"""
        try:
            db = get_db()
            if not db:
                return {"error": "Database connection failed"}
            
            token_ref = db.collection("live_tokens").document(token)
            token_doc = token_ref.get()
            
            if not token_doc.exists:
                return {"error": "Token not found"}
            
            data = token_doc.to_dict()
            
            return {
                "active": data.get("active", False),
                "matches_remaining": data.get("matches_remaining", 0),
                "total_matches": data.get("total_matches", 0),
                "plan_type": data.get("plan_type", "free"),
                "user_id": data.get("user_id")
            }
        except Exception as e:
            print(f"[TOKEN] Error getting token status: {e}")
            return {"error": str(e)}
    
    def revoke_token(self, token: str):
        """Deactivates a token"""
        try:
            db = get_db()
            if not db: return
            
            token_ref = db.collection("live_tokens").document(token)
            token_ref.update({"active": False})
            print(f"[TOKEN] Revoked token: {token}")
        except Exception as e:
            print(f"[TOKEN] Error revoking token: {e}")

token_service = TokenService()
