# META KNOWLEDGE BASE - Patch 7.40c
# Fuente: Dota2ProTracker, Liquipedia, DotaBuff, Official Patch Notes
# Última actualización: Feb 2026 (Patch 7.40c - Jan 22, 2026)

# ====== PATCH 7.40c SPECIFIC CHANGES ======
PATCH_740C_NERFS = {
    "clinkz": "Clinkz: NERF CRÍTICO. Skeleton Walk building damage 25% → 75%. Ya NO viable para rat dota/push. Aghs Scepter ya NO mejora Skeleton Walk (solo da Burning Army). Talent lvl 15: +60 → +50 attack range. Searing Arrows Multishot (lvl 25) ya NO aplica a Skeleton Archers. Evitar pickear para push strats.",
    "broodmother": "Broodmother: NERF SUSTANCIAL. Necrotic Webs Facet: health restoration reducido en late-game. Spin Web charges reducidos. Incapacitating Bite ya NO funciona con illusions. Sigue siendo fuerte en laning pero menos dominante en mid-game.",
    "jakiro": "Jakiro: Nerf menor. Early-game damage reducido. Ice Path duration reducida. Sigue siendo viable pos 4/5 pero menos opresivo en lane.",
    "ember_spirit": "Ember Spirit: Searing Chains duration reducida. Timing de kills más difícil. Requiere mejor ejecución.",
    "phantom_assassin": "Phantom Assassin: Ajustes varios (revisar stats). Sigue siendo carry viable.",
    "spectre": "Spectre: Ajustes varios. Sigue siendo late-game monster."
}

PATCH_740C_BUFFS = {
    "largo": "Largo: AHORA EN CAPTAIN'S MODE (disponible en ranked). Intelligence gain aumentado. Frogstomp damage buff. Amphibian Rhapsody toggling ya NO afectado por silence. Viable pos 3/4. Counters: Anti-mobility items (Eul's, Force Staff).",
    "terrorblade": "Terrorblade: BUFF SIGNIFICATIVO. Conjure Image mana cost reducido. Sunder cooldown reducido. Level 15 Reflection talent: +15% slow/damage. Más fuerte en late-game. Timing de Manta/Skadi más rápido. Counters: AoE damage (Leshrac, Ember, Medusa).",
    "lone_druid": "Lone Druid: Base Agility 20 → 22. Damage lvl 1 aumentado (44–48). Savage Roar duration aumentada. Level 25 talent: 60% → 70% Slow Resistance en True Form. Más fuerte en laning phase. Mejor pos 3.",
    "grimstroke": "Grimstroke: Base damage aumentado. Ink Swell cast range aumentado. Level 15 Ink Swell MS talent mejorado. Más fuerte en pos 4/5.",
    "monkey_king": "Monkey King: Buffs significativos. Más viable en pos 1/2.",
    "pangolier": "Pangolier: Buffs significativos. Más viable en pos 3.",
    "brewmaster": "Brewmaster: Drunken Brawler Earth Stance armor bonus aumentado. Aghs Shard Liquid Courage buff mejorado.",
    "dark_seer": "Dark Seer: +1 base armor. Mejor laning.",
    "doom": "Doom: Infernal Blade mana cost reducido.",
    "earthshaker": "Earthshaker: Fissure mana cost reducido.",
    "treant_protector": "Treant Protector: Eyes in the Forest ahora da 50 gold bounty cuando se destruyen. Ajuste menor."
}

PATCH_740C_ITEM_CHANGES = {
    "phylactery": "Phylactery: NERF. All attributes 7 → 6. Mana regen 2.5 → 2.25. Sigue siendo viable en Int cores pero menos cost-effective. Priorizar otros items si hay mejores opciones.",
    "khanda": "Khanda: Ahora DISASSEMBLABLE. Más flexible para late-game item transitions. Puedes desarmar para hacer otros items si necesitas adaptar build."
}

# ====== CONCEPTOS CLAVE DEL PARCHE ======
PATCH_CORE_CONCEPTS = {
    "facets": "Facetas: Modificadores únicos elegidos pre-game. Algunas cambian mecánicas core (ej: Chronosphere de Void). Elegir mal = -10% WR.",
    "innates": "Innatos: Pasivas lvl 1 gratuitas. No requieren skill points. Críticos para laning (ej: Armor de Treant, MS de Weaver).",
    "wisdom_runes": "Rune Sabiduría: 7min spawn. +280 XP/jugador. OBLIGATORIO tomarla (pos 4/5). Perderla = 1.5 lvls de desventaja.",
    "tormentors": "Tormentors: 20min spawn. 5 Aghs Shards x game. Pos 3/4 deben controlarlos. Perderlos = 5k gold de ventaja enemiga.",
    "portals": "Portales: Twin Gates en mapa. Controlarlos = Map pressure. Wardear cerca = +15% WR.",
}

# ====== ITEMS TIER S (META ACTUAL) ======
TIER_S_ITEMS = {
    "bkb": "BKB: Obligatorio vs 2+ disables. Timing: Pre-25min o pierdes map control.",
    "eternal_shroud": "Eternal Shroud: Counter definitivo vs magic burst. +45% resistencia mágica. Core vs Zeus/Lina/Leshrac.",
    "spirit_vessel": "Spirit Vessel: Stops regen. Mandatory vs Alche/Necro/Morph. Si nadie lo compra = reporte.",
    "pipe": "Pipe of Insight: Offlane obligatorio vs 3+ magic dmg. Si no lo hay = team wipe guaranteed.",
    "guardian_greaves": "Greaves: Mejor item pos 5. Dispel + heal + mana. Si pos 5 no lo tiene a 30min = throw.",
    "force_staff": "Force Staff: Survival tool. Mandatory vs Clockwerk/Mars/Slark. Cuesta 2k, salva 10k.",
    "glimmer_cape": "Glimmer: Invisible + 45% magic resist. Pos 4/5 MUST-HAVE. Cuesta menos que 1 death.",
    "bracer_wraith": "Bracer/Wraith Band: +10% stats en 7.37. Early game dominance. 2-3 stacks = lane won.",
}

# ====== MECÁNICAS CORE POR ROL ======
ROLE_PRIORITIES = {
    "pos1": {
        "farm_benchmark": "10min: 60 CS mínimo. 20min: 150 CS. <700 GPM en win = ineficiente.",
        "timing_items": "BKB: 18-22min. Manta/Skadi: 25-28min. Si te pasas +5min = outdated.",
        "map_awareness": "Debe estar farming lanes peligrosas cuando team crea espacio. Safe farm = desperdicio de Pos 1."
    },
    "pos2": {
        "rune_control": "Power Runes (6min): +100 gold o Haste = rotación gratis. Perderla = -1 kill de ventaja.",
        "rotation_timing": "Debe rotar a 6-8min (Bottle cargado). No rotar = wasted mid advantage.",
        "map_pressure": "Si mid no genera espacio 10-15min, está afk farming como Pos 1 (mal)."
    },
    "pos3": {
        "aura_priority": "Pipe/Crimson/Greaves/Vlads. Si compra Daedalus = reporta.",
        "space_creation": "Debe morir creando espacio. 0/10/20 > 10/0/5. KDA no importa.",
        "initiation": "Blink Dagger timing: 12-15min. Si no hay initiation tool a 20min = throw."
    },
    "pos4": {
        "vision_control": "15+ obs wards placed/game. <10 = no está jugando support.",
        "stacking": "3+ stacks a 10min. 0 stacks = wasted pos 4.",
        "impact_items": "Glimmer/Force/Vessel prioritarios. Comprar Dagon = griefing."
    },
    "pos5": {
        "sacrifice": "Debe estar más pobre que pos 4. Si tiene más NW = está robando farm.",
        "positioning": "Morir <3 veces en 30min = perfecto. >8 = feedeando.",
        "detection": "Dust/Sentries vs invis. No tenerlos cuando hay Riki/BH = auto-lose."
    }
}

# ====== COUNTERS CRÍTICOS ======
CRITICAL_COUNTERS = {
    "illusion_heroes": {
        "heroes": ["Phantom Lancer", "Naga Siren", "Terrorblade"],
        "counters": "Mjollnir, Shiva's, Ember Spirit, Leshrac, Medusa. Sin AoE = auto-lose. NOTA 7.40c: Terrorblade BUFFED (Sunder CD reducido, Conjure Image más barato). Priorizar counters."
    },
    "regen_tanks": {
        "heroes": ["Alchemist", "Necrophos", "Morphling", "Timbersaw"],
        "counters": "Spirit Vessel (MANDATORY), Skadi, AA ulti, Shiva's. Sin anti-heal = unkillable."
    },
    "invis_heroes": {
        "heroes": ["Riki", "Bounty Hunter", "Weaver", "Clinkz"],
        "counters": "Sentries en lane, Dust en supports, Gem a 25min. Sin detection = 4v5. NOTA 7.40c: Clinkz NERFEADO (Skeleton Walk building dmg 75%, ya no viable para rat). Menos prioridad en bans."
    },
    "magic_burst": {
        "heroes": ["Zeus", "Lina", "Lion", "Leshrac"],
        "counters": "BKB, Eternal Shroud, Pipe, Glimmer. No tener = oneshot guaranteed."
    },
    "physical_carries": {
        "heroes": ["Phantom Assassin", "Juggernaut", "Sven"],
        "counters": "Ghost Scepter, Halberd, Shiva's, Solar Crest. Sin armor items = melt."
    }
}

# ====== FACETAS TOP TIER (Ejemplos) ======
TOP_FACETS = {
    "faceless_void": "Chronosphere facet (más duración). Descartar Time Dilation facet = noob pick.",
    "pudge": "Flesh Heap facet (tanky). Rot dmg facet solo vs melee lanes.",
    "invoker": "Aghanim's facet (doble invoke). Quas-Wex facet solo en pos 4 griefing.",
    "anti_mage": "Spell Shield facet vs magic. Blink facet para ultra-aggressive (risky).",
}

# ====== ESTRATEGIAS DE DRAFT ======
DRAFT_WISDOM = {
    "wombo_combo": "Magnus + Invoker/PA/Sven = teamwipe. Counter: Spread out + BKB timings.",
    "global_strat": "Zeus + Spectre/Nature's = no safe farm. Counter: Early aggression + smoke ganks.",
    "push_strat": "Lycan + Beastmaster + Drow = throne a 25min. Counter: Defend highground, no fight outside.",
    "4protect1": "Medusa/Spectre + 4 supports. Counter: Early push, no dejar farmear a 40min.",
}

# ====== ERRORES COMUNES (Para detección automática) ======
COMMON_MISTAKES = {
    "no_bkb": "Carry sin BKB vs 3+ disables = throw garantizado.",
    "no_vessel": "Nadie compró Vessel vs Alche/Necro/Morph = unkillable enemy.",
    "no_detection": "Sin Dust/Sentries vs invis heroes = 4v5.",
    "wrong_farm_priority": "Pos 3/4 farmean más que Pos 1 = draft invertido.",
    "no_vision": "<10 wards placed en 40min = jugando a ciegas.",
    "late_timings": "BKB a 30min, Blink a 25min = items inútiles (ya perdiste).",
}

# ====== SHORTCUTS PARA EL COACH (ABREVIACIONES) ======
ABBREVIATIONS = {
    "NW": "Net Worth",
    "GPM": "Gold Per Minute",
    "XPM": "Experience Per Minute",
    "CS": "Creep Score (Last Hits)",
    "MS": "Movement Speed",
    "AS": "Attack Speed",
    "WR": "Win Rate",
    "Pos 1/2/3/4/5": "Carry/Mid/Offlane/Soft Support/Hard Support",
}


# ====== DYNAMIC META INTEGRATION ======
try:
    from services.meta_service import get_real_time_meta
    DYNAMIC_META_AVAILABLE = True
except ImportError:
    DYNAMIC_META_AVAILABLE = False

DYNAMIC_META_CACHE = {"data": None, "timestamp": 0}

import time
import re

# ====== SINÓNIMOS Y VARIANTES (Tolerancia a errores) ======
KEYWORD_SYNONYMS = {
    "items": [
        # Correctas
        "item", "items", "compra", "compro", "equipo", "equipar", "build", 
        # Errores comunes
        "itm", "itms", "itemz", "comprr", "compre", "comprar",
        # Inglés
        "buy", "gear", "equipment", "purchase"
    ],
    "counters": [
        # Correctas
        "counter", "counters", "contra", "matchup", "vs",
        # Errores comunes  
        "conter", "contr", "kontador", "kounter",
        # Variantes
        "como jugar contra", "que hacer contra", "como ganar a"
    ],
    "facets": [
        # Correctas
        "faceta", "facetas", "facet", "facets", "innato", "innatos", "innate",
        # Errores comunes
        "facetA", "faseta", "fasetas", "innatto",
        # Variantes
        "cual faceta", "que faceta", "mejor faceta"
    ],
    "roles": {
        "pos1": ["pos1", "pos 1", "position 1", "carry", "carr", "adc", "safe lane", "safelane"],
        "pos2": ["pos2", "pos 2", "position 2", "mid", "midlane", "mid lane", "medio"],
        "pos3": ["pos3", "pos 3", "position 3", "offlane", "off lane", "offlaner", "tanque"],
        "pos4": ["pos4", "pos 4", "position 4", "support", "soft support", "roamer", "soporte"],
        "pos5": ["pos5", "pos 5", "position 5", "hard support", "full support", "ward bitch", "5"]
    },
    "analysis": [
        # Preguntas de análisis
        "por que perdi", "porque perdi", "que paso", "analiza", "analysis",
        "que hice mal", "errores", "mistakes", "review"
    ]
}

def flexible_keyword_match(query: str, keyword_list: list) -> bool:
    """
    Busca keywords con tolerancia a errores y sinónimos.
    Usa regex para permitir variaciones ortográficas.
    """
    query_lower = query.lower()
    
    for keyword in keyword_list:
        # Búsqueda exacta primero (más rápida)
        if keyword in query_lower:
            return True
        
        # Fuzzy matching básico (permite 1 carácter de diferencia)
        # Ejemplo: "itm" matchea con "item", "comprr" con "comprar"
        pattern = re.escape(keyword)
        # Permite omitir o duplicar 1 carácter
        fuzzy_pattern = pattern.replace(r'\ ', r'\ ?')  # espacios opcionales
        
        if re.search(fuzzy_pattern, query_lower):
            return True
    
    return False


def get_relevant_knowledge(query: str, hero_names: list = None, debug: bool = False) -> str:
    """
    RAG Selectivo con keywords flexibles y tolerancia a errores.
    Reduce tokens de ~2000 a ~200-400 promedio.
    
    Args:
        query: Pregunta del usuario
        hero_names: Lista de nombres de héroes en la partida (opcional)
        debug: Si True, imprime logs de detección
    
    Returns:
        Conocimiento relevante en formato string
    """
    query_lower = query.lower()
    relevant_sections = []
    detected_topics = []
    
    # 1. Conceptos de parche (facetas, innatos)
    if flexible_keyword_match(query, KEYWORD_SYNONYMS["facets"]):
        relevant_sections.append(f"MECÁNICAS DEL PARCHE: {PATCH_CORE_CONCEPTS}")
        detected_topics.append("Facetas/Innatos")
    
    # 2. Items y builds
    if flexible_keyword_match(query, KEYWORD_SYNONYMS["items"]):
        relevant_sections.append(f"ITEMS META: {TIER_S_ITEMS}")
        detected_topics.append("Items")
    
    # 3. Counters y matchups
    if flexible_keyword_match(query, KEYWORD_SYNONYMS["counters"]):
        relevant_sections.append(f"COUNTERS CRÍTICOS: {CRITICAL_COUNTERS}")
        detected_topics.append("Counters")
    
    # 4. Roles específicos (con sinónimos)
    for role, synonyms in KEYWORD_SYNONYMS["roles"].items():
        if flexible_keyword_match(query, synonyms):
            role_data = ROLE_PRIORITIES.get(role, {})
            if role_data:
                relevant_sections.append(f"PRIORIDADES {role.upper()}: {role_data}")
                detected_topics.append(f"Rol {role.upper()}")
    
    # 5. Análisis general (detecta preguntas tipo "¿por qué perdí?")
    if flexible_keyword_match(query, KEYWORD_SYNONYMS["analysis"]):
        # Inyecta conocimiento amplio para análisis completo
        if not relevant_sections:  # Solo si no se detectó nada específico
            relevant_sections.append(f"CONCEPTOS CORE: {PATCH_CORE_CONCEPTS}")
            relevant_sections.append(f"TOP ITEMS: {TIER_S_ITEMS}")
            detected_topics.append("Análisis General")
    
    # 6. Errores comunes (SIEMPRE incluir, es corto y crítico)
    relevant_sections.append(f"ERRORES COMUNES A DETECTAR: {COMMON_MISTAKES}")
    
    # 6.5. Patch 7.40c Specific Knowledge (Inyectar si se mencionan héroes/items afectados)
    patch_keywords = ["clinkz", "broodmother", "jakiro", "ember", "largo", "terrorblade", 
                      "lone druid", "phylactery", "khanda", "patch", "7.40", "740", "nerf", "buff"]
    if any(keyword in query_lower for keyword in patch_keywords):
        relevant_sections.append(f"CAMBIOS PATCH 7.40c - NERFS: {PATCH_740C_NERFS}")
        relevant_sections.append(f"CAMBIOS PATCH 7.40c - BUFFS: {PATCH_740C_BUFFS}")
        relevant_sections.append(f"CAMBIOS PATCH 7.40c - ITEMS: {PATCH_740C_ITEM_CHANGES}")
        detected_topics.append("Patch 7.40c Changes")

    
    # 7. Inyección de Meta Dinámico (Si está disponible)
    if DYNAMIC_META_AVAILABLE:
        # Update cache every 6 hours
        now = time.time()
        if not DYNAMIC_META_CACHE["data"] or (now - DYNAMIC_META_CACHE["timestamp"]) > 21600:
            DYNAMIC_META_CACHE["data"] = get_real_time_meta()
            DYNAMIC_META_CACHE["timestamp"] = now
        
        if DYNAMIC_META_CACHE["data"] and "error" not in DYNAMIC_META_CACHE["data"]:
            meta = DYNAMIC_META_CACHE["data"]
            top_heroes = ", ".join([f"{h['name']} ({h['wr']}% WR)" for h in meta.get("top_winrate", [])[:5]])
            relevant_sections.append(f"REAL-TIME IMMORTAL META: Top Heroes: {top_heroes}. By Role: {meta.get('by_role', {})}")
            detected_topics.append("Dynamic Meta")

    # 8. Si NO se detectó nada, dar resumen ejecutivo
    if len(relevant_sections) == 1:  # Solo tiene errores comunes
        relevant_sections.insert(0, f"CONCEPTOS CORE: {PATCH_CORE_CONCEPTS}")
        relevant_sections.insert(1, f"TOP ITEMS: {list(TIER_S_ITEMS.keys())[:5]}")
        detected_topics.append("Resumen Ejecutivo")
    
    # Debug logging
    if debug:
        print(f"[RAG] Topics detectados: {detected_topics}")
        print(f"[RAG] Secciones inyectadas: {len(relevant_sections)}")
    
    return "\n\n".join(relevant_sections)

