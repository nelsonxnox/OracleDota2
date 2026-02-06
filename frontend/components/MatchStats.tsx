import React, { useMemo } from 'react';
import { Trophy, Coins, Skull, Target, Award, Zap, Shield, Swords } from 'lucide-react';

interface Player {
    hero_id: number;
    hero_name: string;
    team: string;
    name: string;
    kda: string; // Formato: "kills/deaths/assists"
    networth: number;
    hero_damage: number;
    tower_damage: number;
    hero_healing: number;
    lh_dn: string;
    gpm_xpm: string;
    level: number;
}

interface Metadata {
    winner: string;
    duration_minutes: number;
    radiant_score: number;
    dire_score: number;
    partial_data?: boolean;
}

interface MatchStatsProps {
    players: Player[];
    metadata: Metadata;
}

// Mapeo de hero_id a nombre de imagen (mismo que HeroList.tsx)
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

export default function MatchStats({ players, metadata }: MatchStatsProps) {

    // Helper para parsear KDA de string a números
    const parseKDA = (kda: string) => {
        const parts = kda.split('/').map(n => parseInt(n) || 0);
        return {
            kills: parts[0] || 0,
            deaths: parts[1] || 0,
            assists: parts[2] || 0
        };
    };

    // Calcular el MVP basado en múltiples factores
    const mvp = useMemo(() => {
        const scoredPlayers = players.map(p => {
            const { kills, deaths, assists } = parseKDA(p.kda);
            const kda = (kills + assists) / Math.max(1, deaths);
            const score = (
                kda * 100 +
                p.networth / 100 +
                p.hero_damage / 1000 +
                p.tower_damage / 500 +
                (p.hero_healing || 0) / 500
            );
            return { ...p, score, kills, deaths, assists };
        });
        return scoredPlayers.reduce((prev, current) =>
            prev.score > current.score ? prev : current
        );
    }, [players]);

    // Calcular el net worth final de cada equipo
    const teamNetworth = useMemo(() => {
        const radiant = players
            .filter(p => p.team === 'Radiant')
            .reduce((sum, p) => sum + p.networth, 0);
        const dire = players
            .filter(p => p.team === 'Dire')
            .reduce((sum, p) => sum + p.networth, 0);
        return { radiant, dire };
    }, [players]);

    // Encontrar al jugador con más muertes
    const mostDeaths = useMemo(() => {
        const playersWithDeaths = players.map(p => ({
            ...p,
            ...parseKDA(p.kda)
        }));
        return playersWithDeaths.reduce((prev, current) =>
            prev.deaths > current.deaths ? prev : current
        );
    }, [players]);

    // Encontrar al jugador con más daño a héroes
    const mostHeroDamage = useMemo(() => {
        return players.reduce((prev, current) =>
            prev.hero_damage > current.hero_damage ? prev : current
        );
    }, [players]);

    // Generar frase épica basada en la partida
    const epicPhrase = useMemo(() => {
        const winningTeam = metadata.winner;
        const mvpTeam = mvp.team;
        const duration = metadata.duration_minutes;
        const winScore = metadata.winner === 'Radiant' ? metadata.radiant_score : metadata.dire_score;

        const phrases = [
            `"${mvp.name.toUpperCase()} alzó el trono de ${mvpTeam} con mano de hierro"`,
            `"En ${duration} minutos, ${winningTeam} escribió su leyenda con ${winScore} kills"`,
            `"${mvp.name.toUpperCase()}: El arquitecto de la victoria"`,
            `"La batalla que estremeció el Ancient - ${duration} min de pura adrenalina"`,
        ];

        return phrases[Math.floor(Math.random() * phrases.length)];
    }, [mvp, metadata]);

    const getHeroImage = (heroId: number) => {
        const heroName = HERO_MAP[heroId] || "pudge";
        return `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/${heroName}.png`;
    };

    return (
        <div className="space-y-3">
            {/* MVP Card */}
            <div className="bg-gradient-to-br from-yellow-900/30 via-amber-900/20 to-orange-900/30 border-2 border-yellow-500/40 rounded-xl p-4 relative overflow-hidden shadow-2xl">
                {/* Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/10 to-transparent pointer-events-none" />
                <div className="absolute top-0 right-0 opacity-10">
                    <Trophy size={80} className="text-yellow-500" />
                </div>

                <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-3">
                        <Trophy className="w-5 h-5 text-yellow-400" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-yellow-400">
                            MVP de la Partida
                        </span>
                    </div>

                    <div className="flex items-center gap-3">
                        {/* Hero Avatar */}
                        <div className={`
                            w-14 h-14 rounded-lg overflow-hidden border-2 
                            ${mvp.team === 'Radiant' ? 'border-emerald-400' : 'border-rose-400'}
                            shadow-lg
                        `}>
                            <img
                                src={getHeroImage(mvp.hero_id)}
                                alt={mvp.hero_name}
                                className="w-full h-full object-cover"
                            />
                        </div>

                        {/* Info */}
                        <div className="flex-1">
                            <h3 className="text-base font-black text-yellow-100 uppercase tracking-wide">
                                {mvp.name}
                            </h3>
                            <div className="flex items-center gap-3 mt-1">
                                <span className="text-xs font-bold text-white/80">
                                    {mvp.kills}/{mvp.deaths}/{mvp.assists}
                                </span>
                                <span className="text-[10px] text-yellow-500/70 font-bold">
                                    KDA: {((mvp.kills + mvp.assists) / Math.max(1, mvp.deaths)).toFixed(2)}
                                </span>
                            </div>
                        </div>

                        {/* Trophy Icon */}
                        <div className="flex items-center justify-center">
                            <Award className="w-8 h-8 text-yellow-400 animate-pulse" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Net Worth Final Card */}
            <div className="bg-[#0c0c10] border border-white/5 rounded-xl p-4 shadow-xl">
                <div className="flex items-center gap-2 mb-3">
                    <Coins className="w-4 h-4 text-yellow-500" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">
                        Net Worth Final
                    </span>
                </div>

                <div className="space-y-2">
                    {/* Radiant */}
                    <div className="flex justify-between items-center p-2 bg-emerald-950/20 rounded-lg border border-emerald-500/20">
                        <span className="text-xs font-bold text-emerald-400">Radiant</span>
                        <span className="text-sm font-black text-emerald-300">
                            {(teamNetworth.radiant / 1000).toFixed(1)}k
                        </span>
                    </div>

                    {/* Dire */}
                    <div className="flex justify-between items-center p-2 bg-rose-950/20 rounded-lg border border-rose-500/20">
                        <span className="text-xs font-bold text-rose-400">Dire</span>
                        <span className="text-sm font-black text-rose-300">
                            {(teamNetworth.dire / 1000).toFixed(1)}k
                        </span>
                    </div>
                </div>
            </div>

            {/* Epic Quote Card */}
            <div className="bg-gradient-to-r from-purple-900/20 via-indigo-900/20 to-blue-900/20 border border-indigo-500/30 rounded-xl p-4 relative overflow-hidden shadow-xl">
                <div className="absolute top-0 right-0 opacity-5">
                    <Zap size={60} className="text-indigo-400" />
                </div>

                <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-2">
                        <Swords className="w-4 h-4 text-indigo-400" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">
                            Frase Épica
                        </span>
                    </div>
                    <p className="text-xs italic text-indigo-200/90 leading-relaxed font-medium">
                        {epicPhrase}
                    </p>
                </div>
            </div>

            {/* Most Hero Damage Card */}
            <div className="bg-[#0c0c10] border border-red-500/20 rounded-xl p-4 shadow-xl">
                <div className="flex items-center gap-2 mb-3">
                    <Target className="w-4 h-4 text-red-500" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">
                        Máximo Daño a Héroes
                    </span>
                </div>

                <div className="flex items-center gap-3">
                    <div className={`
                        w-10 h-10 rounded-lg overflow-hidden border-2
                        ${mostHeroDamage.team === 'Radiant' ? 'border-emerald-400' : 'border-rose-400'}
                    `}>
                        <img
                            src={getHeroImage(mostHeroDamage.hero_id)}
                            alt={mostHeroDamage.hero_name}
                            className="w-full h-full object-cover"
                        />
                    </div>

                    <div className="flex-1">
                        <h4 className="text-sm font-bold text-white">{mostHeroDamage.name}</h4>
                        <span className="text-[10px] text-red-400 font-black">
                            {(mostHeroDamage.hero_damage === 0 && metadata.partial_data)
                                ? "Datos NO disponibles"
                                : `${(mostHeroDamage.hero_damage / 1000).toFixed(1)}k de daño`}
                        </span>
                    </div>
                </div>
            </div>

            {/* Most Deaths (Fun Stat) */}
            <div className="bg-[#0c0c10] border border-zinc-700/30 rounded-xl p-4 shadow-xl">
                <div className="flex items-center gap-2 mb-3">
                    <Skull className="w-4 h-4 text-zinc-500" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-zinc-600">
                        Alimentó más al enemigo
                    </span>
                </div>

                <div className="flex items-center gap-3">
                    <div className={`
                        w-10 h-10 rounded-lg overflow-hidden border-2 border-zinc-600/50
                    `}>
                        <img
                            src={getHeroImage(mostDeaths.hero_id)}
                            alt={mostDeaths.hero_name}
                            className="w-full h-full object-cover grayscale"
                        />
                    </div>

                    <div className="flex-1">
                        <h4 className="text-sm font-bold text-zinc-400">{mostDeaths.name}</h4>
                        <span className="text-[10px] text-zinc-500 font-black">
                            {mostDeaths.deaths} muertes
                        </span>
                    </div>
                </div>
            </div>

            {/* Game Duration Card */}
            <div className="bg-gradient-to-br from-slate-900/50 to-zinc-900/50 border border-white/5 rounded-xl p-4 shadow-xl">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="text-[10px] font-black uppercase tracking-widest text-zinc-500 mb-1">
                            Duración
                        </div>
                        <div className="text-2xl font-black text-white">
                            {metadata.duration_minutes} <span className="text-sm text-zinc-500">min</span>
                        </div>
                    </div>
                    <div className={`
                        px-4 py-2 rounded-lg font-black text-xs uppercase tracking-wider
                        ${metadata.winner === 'Radiant'
                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                            : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'}
                    `}>
                        {metadata.winner} Ganó
                    </div>
                </div>
            </div>
        </div>
    );
}
