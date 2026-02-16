import os
import sys

# Agregar el directorio raíz al path para que encuentre el paquete 'backend'
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from backend.knowledge import get_relevant_knowledge
from backend.services.ai_coach import oracle

def test_rag():
    print("=== TEST RAG SYSTEM START ===")
    
    # Test 1: Basic retrieval
    query = "counter de meepo"
    print(f"\n[TEST 1] Query: '{query}'")
    try:
        knowledge = get_relevant_knowledge(query, debug=True)
        print(f"[RESULT] Knowledge retrieved ({len(knowledge)} chars):")
        print(knowledge[:500] + "..." if len(knowledge) > 500 else knowledge)
        
        if "Earthshaker" in knowledge or "Winter Wyvern" in knowledge:
            print("[SUCCESS] Relevant counters found.")
        else:
            print("[FAILURE] Expected counters not found.")
            
    except Exception as e:
        print(f"[ERROR] {e}")

    # Test 2: AI Integration (using new key)
    print(f"\n[TEST 2] AI Integration with new key")
    try:
        # Mock context
        context = "Match ID: 123456789\nHero: Anti-Mage\nTime: 15:00\nNetworth: 8000\nKDA: 3/1/2"
        query = "Como counterear a Meepo?"
        
        response = oracle.ask_oracle("", query, debug=True)
        if "Error final" in response:
             print(f"[FAILURE] AI error: {response}")
        else:
             print(f"[SUCCESS] AI Response: {response[:100]}...")
             
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_rag()
