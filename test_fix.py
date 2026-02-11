import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from services.token_service import token_service
from services.firebase_service import get_db

def test():
    print("Testing TokenService initialization...")
    try:
        db = get_db()
        if db:
            print("Firebase DB initialized successfully.")
            # Test getting a token (should not crash even if user doesn't exist)
            token = token_service.get_user_token("test_user_id")
            print(f"Token retrieved (or None): {token}")
            print("Verification SUCCESS.")
        else:
            print("Firebase DB initialization FAILED (returned None).")
    except Exception as e:
        print(f"Verification FAILED with error: {e}")

if __name__ == "__main__":
    test()
