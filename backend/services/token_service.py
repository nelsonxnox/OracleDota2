import uuid
from datetime import datetime
from services.firebase_service import db

class TokenService:
    """Manages live coaching tokens for user authentication"""
    
    def generate_live_token(self, user_id: str) -> str:
        """
        Generates a unique token for a user's live coaching session.
        If user already has a token, returns the existing one.
        """
        if not user_id or user_id == "guest":
            raise ValueError("Guest users cannot use live coaching")
        
        # Check if user already has a token
        existing_token = self.get_user_token(user_id)
        if existing_token:
            print(f"[TOKEN] User {user_id} already has token, returning existing")
            return existing_token
        
        # Generate new token
        token = str(uuid.uuid4())
        
        # Store in Firestore
        try:
            from google.cloud import firestore
            
            token_ref = db.collection("live_tokens").document(token)
            token_ref.set({
                "user_id": user_id,
                "created_at": firestore.SERVER_TIMESTAMP,
                "active": True
            })
            
            # Also store reference in user doc for easy lookup
            user_ref = db.collection("users").document(user_id)
            user_ref.set({"live_token": token}, merge=True)
            
            print(f"[TOKEN] Generated new token for user {user_id}")
            return token
        except Exception as e:
            print(f"[TOKEN] Error generating token: {e}")
            raise
    
    def get_user_token(self, user_id: str) -> str | None:
        """Retrieves existing token for a user"""
        try:
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
        Returns None if token is invalid.
        """
        try:
            token_ref = db.collection("live_tokens").document(token)
            token_doc = token_ref.get()
            
            if not token_doc.exists:
                print(f"[TOKEN] Invalid token: {token}")
                return None
            
            data = token_doc.to_dict()
            if not data.get("active", False):
                print(f"[TOKEN] Inactive token: {token}")
                return None
            
            user_id = data.get("user_id")
            print(f"[TOKEN] Valid token for user: {user_id}")
            return user_id
        except Exception as e:
            print(f"[TOKEN] Error validating token: {e}")
            return None
    
    def revoke_token(self, token: str):
        """Deactivates a token"""
        try:
            token_ref = db.collection("live_tokens").document(token)
            token_ref.update({"active": False})
            print(f"[TOKEN] Revoked token: {token}")
        except Exception as e:
            print(f"[TOKEN] Error revoking token: {e}")

token_service = TokenService()
