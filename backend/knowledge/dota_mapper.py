"""
DotaConstants Mapper
Convierte IDs numéricos de la API a nombres legibles usando dotaconstants.
"""
import json
import os

# Paths relativos a este archivo
BASE_DIR = os.path.dirname(__file__)
HEROES_PATH = os.path.join(BASE_DIR, "heroes.json")
ITEMS_PATH = os.path.join(BASE_DIR, "items.json")
ABILITIES_PATH = os.path.join(BASE_DIR, "abilities.json")

class DotaMapper:
    def __init__(self):
        self.heroes = {}
        self.items = {}
        self.abilities = {}
        self._load_data()
    
    def _load_data(self):
        """Carga los JSONs de dotaconstants"""
        try:
            if os.path.exists(HEROES_PATH):
                with open(HEROES_PATH, 'r', encoding='utf-8') as f:
                    self.heroes = json.load(f)
            
            if os.path.exists(ITEMS_PATH):
                with open(ITEMS_PATH, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
            
            if os.path.exists(ABILITIES_PATH):
                with open(ABILITIES_PATH, 'r', encoding='utf-8') as f:
                    self.abilities = json.load(f)
            
            print(f"[DotaMapper] Loaded: {len(self.heroes)} heroes, {len(self.items)} items, {len(self.abilities)} abilities")
        except Exception as e:
            print(f"[DotaMapper] Warning: Could not load constants: {e}")
    
    def get_hero_name(self, hero_id: int) -> str:
        """Convierte hero_id a nombre legible"""
        hero_id_str = str(hero_id)
        if hero_id_str in self.heroes:
            return self.heroes[hero_id_str].get("localized_name", f"Hero_{hero_id}")
        return f"Unknown_Hero_{hero_id}"
    
    def get_item_name(self, item_id: int) -> str:
        """Convierte item_id a nombre legible"""
        item_id_str = str(item_id)
        if item_id_str in self.items:
            return self.items[item_id_str].get("dname", f"Item_{item_id}")
        return f"Unknown_Item_{item_id}"
    
    def get_ability_name(self, ability_id: int) -> str:
        """Convierte ability_id a nombre legible"""
        ability_id_str = str(ability_id)
        if ability_id_str in self.abilities:
            return self.abilities[ability_id_str].get("dname", f"Ability_{ability_id}")
        return f"Unknown_Ability_{ability_id}"
    
    def enrich_match_data(self, match_data: dict) -> dict:
        """
        Enriquece los datos de la partida con nombres legibles.
        Esto ayuda a que la IA entienda mejor sin necesidad de IDs.
        """
        # Añadir nombres de héroes a los jugadores
        if "players" in match_data:
            for player in match_data["players"]:
                if "hero_id" in player:
                    player["hero_name"] = self.get_hero_name(player["hero_id"])
        
        return match_data

# Singleton global
mapper = DotaMapper()
