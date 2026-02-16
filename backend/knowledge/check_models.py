import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("Error: OPENROUTER_API_KEY not found in .env")
    exit(1)

try:
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total models found: {len(data['data'])}")
        
        print("\n--- FREE MODELS ---")
        free_models = []
        for model in data['data']:
            # Check for free pricing (some models use 'pricing' object)
            pricing = model.get('pricing', {})
            prompt = float(pricing.get('prompt', 0))
            completion = float(pricing.get('completion', 0))
            
            if prompt == 0 and completion == 0:
                free_models.append(model['id'])
                print(f"- {model['id']}")
                
        if not free_models:
            print("No completely free models found. Checking for 'free' in ID...")
            for model in data['data']:
                if ":free" in model['id']:
                    print(f"- {model['id']} (ID contains ':free')")

    else:
        print(f"Error fetching models: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Error: {e}")
