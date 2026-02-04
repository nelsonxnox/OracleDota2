import requests
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

STRATZ_API_URL = "https://api.stratz.com/graphql"
STRATZ_API_KEY = os.getenv("STRATZ_API_KEY")

class StratzService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or STRATZ_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}

    def query(self, query_str: str, variables: Dict = None) -> Dict:
        """Executes a GraphQL query against Stratz API."""
        if not self.api_key:
            return {"error": "Stratz API Key not found. Please set STRATZ_API_KEY in .env"}
            
        try:
            response = requests.post(
                STRATZ_API_URL,
                json={"query": query_str, "variables": variables},
                headers=self.headers,
                timeout=20
            )
            if response.status_code != 200:
                return {"error": f"Stratz API Error: {response.status_code}", "detail": response.text}
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_match_laning_data(self, match_id: str) -> Dict:
        """Fetches AI-calculated lane outcomes and win probability."""
        gql_query = """
        query($matchId: Long!) {
          match(id: $matchId) {
            didRadiantWin
            durationSeconds
            winProbability {
              time
              radiantWinProbability
            }
            lanes {
              lane
              outcome
              roshans {
                time
                isRadiant
              }
            }
            players {
              playerSlot
              impulse
              laneOutcome
            }
          }
        }
        """
        result = self.query(gql_query, {"matchId": int(match_id)})
        if "error" in result:
            return result
        
        return result.get("data", {}).get("match", {})

    def format_stratz_context(self, stratz_data: Dict) -> str:
        """Formats Stratz data for the AI context."""
        if not stratz_data or "error" in stratz_data:
            return "Información de Stratz no disponible (Falta API Key o error de conexión)."

        context = ["\n--- ANÁLISIS AVANZADO (STRATZ AI) ---"]
        
        # Lane Outcomes
        lanes = stratz_data.get("lanes", [])
        for i, lane in enumerate(lanes):
            lane_name = {1: "Safe", 2: "Mid", 3: "Off"}.get(lane.get("lane"), "Unknown")
            outcome = lane.get("outcome", "N/A")
            context.append(f"Carril {lane_name}: Resultado {outcome}")

        # Win Probability
        win_prob = stratz_data.get("winProbability", [])
        if win_prob:
            # Get last recorded win prob
            last_prob = win_prob[-1]
            radiant_prob = round(last_prob.get("radiantWinProbability", 0.5) * 100, 1)
            context.append(f"Probabilidad de Victoria Final: Radiant {radiant_prob}% | Dire {100-radiant_prob}%")

        # Impulses (Performance index)
        players = stratz_data.get("players", [])
        high_impulses = []
        for p in players:
            impulse = p.get("impulse")
            if impulse and impulse > 0:
                # We'd need to map playerSlot to hero name for better context, 
                # but we'll let the AI handle the slot mapping if it has OpenDota data.
                high_impulses.append(f"Slot {p['playerSlot']}: Impulse {impulse}")
        
        if high_impulses:
            context.append(f"Impulso de Desempeño: {', '.join(high_impulses)}")

        return "\n".join(context)

# Singleton
stratz = StratzService()
