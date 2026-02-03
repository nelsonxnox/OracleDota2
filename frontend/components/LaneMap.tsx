import React, { useMemo } from 'react';
import { Card } from "@/components/ui/card";

interface Player {
    hero_id: number;
    hero_name: string;
    team: string;
    lane_role: number;
    name: string;
    movement_history?: { [minute: number]: { x: number, y: number } };
}

interface LaneMapProps {
    players: Player[];
    currentTime?: number; // Minuto actual para replay
}

// Mapeo de hero_id a nombre de imagen (igual que HeroList.tsx)
const HERO_MAP: { [key: number]: string } = {
    1: "antimage", 2: "axe", 3: "bane", 4: "bloodseeker", 5: "crystal_maiden",
    6: "drow_ranger", 7: "earthshaker", 8: "juggernaut", 9: "mirana", 10: "morphling",
    11: "nevermore", 12: "phantom_lancer", 13: "puck", 14: "pudge", 15: "razor",
    16: "sand_king", 17: "storm_spirit", 18: "sven", 19: "tiny", 20: "vengefulspirit",
    21: "windrunner", 22: "zuus", 23: "kunkka", 25: "lina", 26: "lion",
    27: "shadow_shaman", 28: "slardar", 29: "tidehunter", 30: "witch_doctor", 31: "lich",
    32: "riki", 33: "enigma", 34: "tinker", 35: "sniper", 36: "necrolyte",
    37: "warlock", 38: "beastmaster", 39: "queenofpain", 40: "venomancer", 41: "faceless_void",
    42: "skeleton_king", 43: "death_prophet", 44: "phantom_assassin", 45: "pugna", 46: "templar_assassin",
    47: "viper", 48: "luna", 49: "dragon_knight", 50: "dazzle", 51: "rattletrap",
    52: "leshrac", 53: "furion", 54: "life_stealer", 55: "dark_seer", 56: "clinkz",
    57: "omniknight", 58: "enchantress", 59: "huskar", 60: "night_stalker", 61: "broodmother",
    62: "bounty_hunter", 63: "weaver", 64: "jakiro", 65: "batrider", 66: "chen",
    67: "spectre", 68: "ancient_apparition", 69: "doom_bringer", 70: "ursa", 71: "spirit_breaker",
    72: "gyrocopter", 73: "alchemist", 74: "invoker", 75: "silencer", 76: "obsidian_destroyer",
    77: "lycan", 78: "brewmaster", 79: "shadow_demon", 80: "lone_druid", 81: "chaos_knight",
    82: "meepo", 83: "treant", 84: "ogre_magi", 85: "undying", 86: "rubick",
    87: "disruptor", 88: "nyx_assassin", 89: "naga_siren", 90: "keeper_of_the_light", 91: "wisp",
    92: "visage", 93: "slark", 94: "medusa", 95: "troll_warlord", 96: "centaur",
    97: "magnataur", 98: "shredder", 99: "bristleback", 100: "tusk", 101: "skywrath_mage",
    102: "abaddon", 103: "elder_titan", 104: "legion_commander", 105: "techies", 106: "ember_spirit",
    107: "earth_spirit", 108: "abyssal_underlord", 109: "terrorblade", 110: "phoenix", 111: "oracle",
    112: "winter_wyvern", 113: "arc_warden", 114: "monkey_king", 119: "dark_willow", 120: "pangolier",
    121: "grimstroke", 123: "hoodwink", 126: "void_spirit", 128: "snapfire", 129: "mars",
    135: "dawnbreaker", 136: "marci", 137: "primal_beast", 138: "muerta"
};

export default function LaneMap({ players, currentTime = -1 }: LaneMapProps) {

    const getPosition = (p: Player, indexInLane: number) => {
        const isRadiant = p.team === "Radiant"; // Moved this definition to the top

        // 1. REPLAY MODE: Si hay un tiempo seleccionado y datos de movimiento
        if (currentTime >= 0) {
            if (p.movement_history) {
                // Buscar la posición más cercana
                let pos = p.movement_history[currentTime];

                // Si no hay dato exacto, buscar hacia atrás
                if (!pos) {
                    for (let m = currentTime - 1; m >= Math.max(0, currentTime - 5); m--) {
                        if (p.movement_history[m]) {
                            pos = p.movement_history[m];
                            break;
                        }
                    }
                }

                if (pos) {
                    // Coordenadas OpenDota lane_pos suelen ser 0-128
                    // Convertir a porcentajes CSS (0-100%)
                    // X: 0 (Izquierda) -> 128 (Derecha)
                    // Y: 128 (Arriba - en lógica dota Y crece hacia arriba) -> 0 (Abajo)
                    // PERO en CSS "top" 0 es Arriba.
                    // Así que Top% = (128 - y) / 128 * 100

                    const x_pct = (pos.x / 128) * 100;
                    const y_pct = ((128 - pos.y) / 128) * 100;

                    return { top: `${y_pct}%`, left: `${x_pct}%` };
                }
            }
            // Si no hay datos de movimiento, quedarse en la base o mostrar en base
            // Esto confirma al usuario que no hay datos, en lugar de inventar una posición
            // Fallback to base to indicate "No Data" cleanly
            return { top: isRadiant ? '95%' : '5%', left: isRadiant ? '5%' : '95%' };
        }

        // 2. STATIC MODE (Default): Posiciones iniciales por Lane
        // Offset AUMENTADO para mejor separación entre héroes
        const offset = indexInLane * 10;

        let top = 50;
        let left = 50;

        switch (p.lane_role) {
            case 1: // SAFE LANE (Radiant: Bot-Right / Dire: Top-Left)
                if (isRadiant) {
                    // Radiant Safe Lane -> Bottom Right corner
                    top = 85;
                    left = 82 - offset;
                } else {
                    // Dire Safe Lane -> Top Left corner
                    top = 15 + offset;
                    left = 18;
                }
                break;
            case 2: // MID LANE - Central diagonal
                // Héroes en mid van por la diagonal central
                if (isRadiant) {
                    top = 55 + (indexInLane * 3);
                    left = 45 - (indexInLane * 3);
                } else {
                    top = 45 - (indexInLane * 3);
                    left = 55 + (indexInLane * 2);
                }
                break;
            case 3: // OFF LANE (Radiant: Top-Left / Dire: Bot-Right)
                if (isRadiant) {
                    // Radiant Off Lane -> Top Left
                    top = 18 + offset;
                    left = 15;
                } else {
                    // Dire Off Lane -> Bottom Right
                    top = 82;
                    left = 85 - offset;
                }
                break;
            case 4: // JUNGLE
                if (isRadiant) {
                    // Radiant Jungle -> Bottom-center area
                    top = 68 + (indexInLane * 3);
                    left = 32 + (indexInLane * 3);
                } else {
                    // Dire Jungle -> Top-center area
                    top = 32 - (indexInLane * 3);
                    left = 68 - (indexInLane * 3);
                }
                break;
            default:
                // Fallback: bases
                top = isRadiant ? 95 : 5;
                left = isRadiant ? 5 : 95;
        }

        return { top: `${top}%`, left: `${left}%` };
    };

    const positionedPlayers = useMemo(() => {
        const laneCounts: { [key: string]: number } = {};
        return players.map(p => {
            // Solo incrementar offset en modo estático
            const isReplay = currentTime >= 0 && p.movement_history && p.movement_history[currentTime];

            const key = `${p.team}-${p.lane_role}`;
            const idx = isReplay ? 0 : (laneCounts[key] || 0); // No offset en replay mode

            if (!isReplay) laneCounts[key] = idx + 1;

            return { ...p, position: getPosition(p, idx) };
        });
    }, [players, currentTime]);

    return (
        <Card className="w-full aspect-square bg-zinc-900 border-zinc-800 relative overflow-hidden shadow-2xl rounded-xl">
            {/* FONDO DEL MAPA DE DOTA 2 - IMAGEN LOCAL */}
            <div className="absolute inset-0 z-0">
                <img
                    src="/minimap.png"
                    alt="Dota 2 Minimap"
                    className="w-full h-full object-cover"
                    style={{
                        filter: 'brightness(0.7) contrast(1.15)',
                        imageRendering: 'crisp-edges'
                    }}
                    onError={(e) => {
                        // Fallback a fondo degradado oscuro si la imagen local no existe
                        console.error('Minimap image not found at /minimap.png');
                        (e.target as HTMLImageElement).style.display = 'none';
                    }}
                />
                {/* Overlay para mejor contraste con los iconos */}
                <div className="absolute inset-0 bg-gradient-to-br from-black/25 via-transparent to-black/25" />
            </div>

            {/* LÍNEAS DE LAS LANES - Guía visual */}
            <div className="absolute inset-0 z-5 opacity-15 pointer-events-none">
                {/* Diagonal principal (Mid Lane) */}
                <div className="absolute inset-0" style={{
                    background: 'linear-gradient(135deg, transparent 48.5%, rgba(100,200,255,0.4) 49%, rgba(100,200,255,0.4) 51%, transparent 51.5%)'
                }} />
            </div>

            {/* CAPA DE HÉROES - MÁS PEQUEÑOS */}
            <div className="absolute inset-0 z-10">
                {positionedPlayers.map((p, i) => {
                    // Usar HERO_MAP para obtener el nombre correcto de la imagen
                    const heroImageName = HERO_MAP[p.hero_id] || "pudge";
                    const isRadiant = p.team === "Radiant";

                    return (
                        <div
                            key={i}
                            className="absolute w-8 h-8 group cursor-pointer hover:z-50 transition-all duration-200"
                            style={{
                                top: p.position.top,
                                left: p.position.left,
                                transform: 'translate(-50%, -50%)'
                            }}
                            title={`${p.name} - ${p.hero_name}`}
                        >
                            {/* Hero Icon Container */}
                            <div className={`
                                w-full h-full rounded-full border-2 overflow-hidden bg-black/90 
                                group-hover:scale-125 group-hover:border-[2.5px] transition-all duration-200
                                ${isRadiant
                                    ? "border-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)] group-hover:shadow-[0_0_15px_rgba(52,211,153,1)]"
                                    : "border-rose-400 shadow-[0_0_10px_rgba(251,113,133,0.8)] group-hover:shadow-[0_0_15px_rgba(251,113,133,1)]"}
                            `}>
                                <img
                                    src={`https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/${heroImageName}.png`}
                                    alt={p.hero_name}
                                    className="w-full h-full object-cover scale-110 brightness-110"
                                    onError={(e) => {
                                        console.error(`Error loading hero image for ${p.hero_name} (ID: ${p.hero_id})`);
                                        (e.target as HTMLImageElement).src = 'https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png';
                                    }}
                                />
                            </div>

                            {/* Lane Role Indicator - Badge proporcional */}
                            <div className={`
                                absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full text-[7px] font-black 
                                flex items-center justify-center border border-black/80
                                ${isRadiant ? 'bg-emerald-500 text-black' : 'bg-rose-500 text-white'}
                                opacity-0 group-hover:opacity-100 transition-opacity
                            `}>
                                {p.lane_role === 1 ? 'S' : p.lane_role === 2 ? 'M' : p.lane_role === 3 ? 'O' : 'J'}
                            </div>

                            {/* Name Label on Hover */}
                            <div className="absolute -bottom-7 left-1/2 -translate-x-1/2 bg-black/95 text-white text-[9px] px-2.5 py-1 rounded-md opacity-0 group-hover:opacity-100 whitespace-nowrap pointer-events-none transition-opacity z-50 font-bold uppercase tracking-wide border border-white/20 shadow-xl">
                                {p.name}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Team Labels - Mejorados */}
            <div className="absolute bottom-2 left-2 z-0 text-[11px] font-black text-emerald-400/40 uppercase tracking-widest pointer-events-none drop-shadow-lg">Radiant</div>
            <div className="absolute top-2 right-2 z-0 text-[11px] font-black text-rose-400/40 uppercase tracking-widest pointer-events-none drop-shadow-lg">Dire</div>

            {/* Corner Glow Effects */}
            <div className="absolute bottom-0 left-0 w-20 h-20 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />
            <div className="absolute top-0 right-0 w-20 h-20 bg-rose-500/10 rounded-full blur-2xl pointer-events-none" />
        </Card>
    );
}
