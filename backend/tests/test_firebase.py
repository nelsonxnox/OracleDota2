import os
import sys
from dotenv import load_dotenv

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

load_dotenv()

from services import firebase_service

def test_firebase():
    print("--- TESTING FIREBASE CONNECTION ---")
    db = firebase_service.get_db()
    if db:
        print("RESULT: FIREBASE SUCCESS")
        # Try to list collections as a real test
        try:
            collections = [c.id for c in db.collections()]
            print(f"Collections found: {collections}")
        except Exception as e:
            print(f"Error listing collections: {e}")
    else:
        print("RESULT: FIREBASE FAILED")

if __name__ == "__main__":
    test_firebase()
