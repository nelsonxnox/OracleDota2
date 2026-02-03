"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Shield, Swords, Coins, TrendingUp, Zap, Target } from "lucide-react";
import { motion } from "framer-motion";

interface Player {
    name: string;
    team: string;
    hero_id: number;
    kda: string;
    networth: number;
    lh_dn: string;
    gpm_xpm: string;
    hero_damage: number;
    tower_damage: number;
    level: number;
    item_timings?: { item_name: string; time: number }[];
}

interface HeroListProps {
    players: Player[];
}

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

export default function HeroList({ players, teamFilter }: HeroListProps & { teamFilter?: "Radiant" | "Dire" }) {
    const getHeroImage = (heroId: number) => {
        const name = HERO_MAP[heroId] || "pudge";
        return `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/${name}.png`;
    };

    const maxNetworth = Math.max(...players.map(p => p.networth));

    const RenderTeam = ({ teamName, players }: { teamName: string, players: Player[] }) => (
        <div className="space-y-4">
            <div className="flex items-center justify-between px-2 pb-2 border-b border-white/5">
                <div className="flex items-center gap-3">
                    <div className={`h-1.5 w-8 rounded-full ${teamName === "Radiant" ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]"}`} />
                    <h3 className={`text-xs font-black uppercase tracking-[0.2em] italic ${teamName === "Radiant" ? "text-emerald-100" : "text-rose-100"}`}>{teamName} Forces</h3>
                </div>
                <span className="text-[9px] font-black italic text-zinc-500 tabular-nums">NW: {(players.reduce((a, b) => a + b.networth, 0) / 1000).toFixed(1)}k</span>
            </div>

            <div className="grid gap-4">
                {players.map((p, i) => (
                    <div key={i} className="group relative overflow-hidden rounded-xl bg-zinc-900/40 border border-white/5 hover:border-teal-500/30 hover:bg-zinc-800/60 transition-all p-3">
                        {/* Expanded Layout */}
                        <div className="flex items-center gap-4">
                            {/* Hero Avatar */}
                            <div className="relative h-14 w-20 shrink-0 overflow-hidden rounded-lg border border-white/10 shadow-lg">
                                <img src={getHeroImage(p.hero_id)} alt="Hero" className="object-cover w-full h-full scale-110" />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
                                <div className="absolute bottom-1 left-1.5 flex items-center gap-1">
                                    <span className="text-[10px] font-black text-white px-1 bg-black/50 rounded">LVL {p.level}</span>
                                </div>
                            </div>

                            {/* Info & Stats Grid */}
                            <div className="flex-1 min-w-0 grid grid-cols-2 gap-x-4 gap-y-1">
                                <div className="col-span-1">
                                    <h4 className="text-xs font-black text-zinc-100 truncate group-hover:text-teal-400 transition-colors uppercase tracking-tight">{p.name || "Unknown"}</h4>
                                    <span className="text-[11px] font-mono font-bold text-zinc-500 flex items-center gap-1.5">
                                        <Swords size={10} className="text-rose-500/70" /> {p.kda}
                                    </span>
                                </div>

                                <div className="col-span-1 border-l border-white/5 pl-4 flex flex-col justify-center">
                                    <div className="flex items-center justify-between text-[10px] mb-0.5">
                                        <span className="text-zinc-500 font-bold uppercase tracking-tighter flex items-center gap-1"><Coins size={10} className="text-yellow-500/70" /> NW</span>
                                        <span className="text-zinc-200 font-black">{(p.networth / 1000).toFixed(1)}k</span>
                                    </div>
                                    <div className="flex items-center justify-between text-[10px]">
                                        <span className="text-zinc-500 font-bold uppercase tracking-tighter flex items-center gap-1"><Zap size={10} className="text-teal-500/70" /> DMG</span>
                                        <span className="text-zinc-200 font-black">{(p.hero_damage / 1000).toFixed(1)}k</span>
                                    </div>
                                </div>

                                <div className="col-span-2 mt-2">
                                    {/* Progress Bar (Networth vs Team Max) */}
                                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${(p.networth / maxNetworth) * 100}%` }}
                                            className={`h-full ${teamName === "Radiant" ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" : "bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.4)]"}`}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

        </div>
    );

    const filteredPlayers = teamFilter
        ? players.filter(p => p.team === teamFilter)
        : players;

    // Si hay filtro, renderizamos solo ese equipo directamente
    if (teamFilter) {
        return <RenderTeam teamName={teamFilter} players={filteredPlayers} />;
    }

    // Comportamiento Legacy (Ambos equipos)
    return (
        <div className="space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <RenderTeam teamName="Radiant" players={players.filter(p => p.team === "Radiant")} />
            <RenderTeam teamName="Dire" players={players.filter(p => p.team === "Dire")} />
        </div>
    );
}
