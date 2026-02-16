import os
import sys
from dotenv import load_dotenv

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

load_dotenv()

from services.ai_coach import oracle

def test_oracle_quality():
    print("--- TESTING ORACLE RESPONSE QUALITY ---")
    
    test_context = "PARTIDA #12345 | GANO: Radiant | DURACION: 35m\nEQUIPOS: Radiant (Anti-Mage, Largo) vs Dire (Pudge, Zeus)"
    test_query = "Dime que items debo comprar contra Zeus si soy Anti-Mage y voy perdiendo."
    
    print(f"Query: {test_query}")
    print("Waiting for response...")
    
    try:
        # Habilitar debug para ver cada intento de modelo
        response = oracle.ask_oracle(test_context, test_query, debug=True)
        print("\n--- FINAL RESPONSE ---")
        print(response)
        print("----------------------\n")
        
        # Save to file for inspection
        with open("d:\\Proyectos de Informatica\\proyecto de dota 2\\backend\\tests\\last_response.txt", "w", encoding="utf-8") as f:
            f.write(response)
        
        # 1. Check for Markdown
        markdown_chars = ['*', '_', '#', '`']
        has_markdown = any(char in response for char in markdown_chars)
        
        # 2. Check for Spanish (simple heuristic)
        spanish_keywords = ["comprar", "contra", "items", "porque", "debes", "táctico", "malla", "victoria"]
        is_spanish = any(word in response.lower() for word in spanish_keywords)
        
        # 3. Check for sanity (no nonsense words found in previous failure)
        nonsense_words = ["masmajera", "tellalarra", "inequibrado", "tellelarra"]
        has_nonsense = any(word in response.lower() for word in nonsense_words)
        
        print(f"Markdown check: {'FAIL' if has_markdown else 'PASS'}")
        print(f"Spanish check: {'PASS' if is_spanish else 'FAIL'}")
        print(f"Sanity check: {'FAIL' if has_nonsense else 'PASS'}")
        
        if not has_markdown and is_spanish and not has_nonsense:
            print("\nRESULT: SUCCESS")
        else:
            print("\nRESULT: FAILED")
            
    except Exception as e:
        import traceback
        print(f"ERROR during test: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_oracle_quality()
