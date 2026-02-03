"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
    Sparkles,
    ChevronLeft,
    History,
    Sword,
    Skull,
    UserPlus,
    TrendingUp,
    Clock,
    ExternalLink,
    Info,
    Trophy,
    Shield
} from "lucide-react";
import { motion } from "framer-motion";
import { API_BASE } from "@/lib/api";

interface PlayerInfo {
    account_id: string;
    personaname: string;
    avatar: string;
    rank_tier: number | null;
    leaderboard_rank: number | null;
}

interface Match {
    match_id: string;
    hero: string;
    hero_img: string;
    result: "Win" | "Loss";
    kda: string;
    start_time: number;
    duration: string;
}

const getRankName = (tier: number | null) => {
    if (!tier) return "Unranked";
    const ranks = ["Herald", "Guardian", "Crusader", "Archon", "Legend", "Ancient", "Divine", "Immortal"];
    const firstDigit = Math.floor(tier / 10);
    const star = tier % 10;

    if (firstDigit >= 8) return "Immortal";
    if (firstDigit === 0) return "Unranked";
    return `${ranks[firstDigit - 1]} ${star}`;
};

export default function PlayerProfile() {
    const params = useParams();
    const id = params.id as string;
    const router = useRouter();

    const [player, setPlayer] = useState<PlayerInfo | null>(null);
    const [matches, setMatches] = useState<Match[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshing, setRefreshing] = useState(false);
    const [refreshMsg, setRefreshMsg] = useState("");

    const fetchData = async () => {
        try {
            setLoading(true);
            setError(null);
            const infoRes = await fetch(`${API_BASE}/player/${id}/info`);
            const infoData = await infoRes.json();

            if (infoData.error) {
                setError(infoData.error);
                return;
            }
            setPlayer(infoData);

            const matchesRes = await fetch(`${API_BASE}/player/${id}/latest`);
            const matchesData = await matchesRes.json();
            setMatches(matchesData.matches || []);
        } catch (err) {
            setError("Error de conexión con el servidor");
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = async () => {
        try {
            setRefreshing(true);
            const res = await fetch(`${API_BASE}/player/${id}/refresh`, { method: "POST" });
            const data = await res.json();
            setRefreshMsg("Sincronización solicitada. Espera unos segundos...");
            setTimeout(() => {
                setRefreshMsg("");
                fetchData();
            }, 3000);
        } catch (err) {
            setRefreshMsg("Error al sincronizar");
        } finally {
            setRefreshing(false);
        }
    };

    useEffect(() => {
        if (id) fetchData();
    }, [id]);

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex flex-col items-center justify-center text-white">
                <div className="h-16 w-16 border-4 border-red-600/20 border-t-red-600 rounded-full animate-spin mb-4" />
                <p className="text-xs font-black uppercase tracking-[0.3em] animate-pulse">Consultando el Oráculo...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-black flex flex-col items-center justify-center text-white p-6">
                <div className="bg-red-900/20 border border-red-600/30 p-8 rounded-2xl text-center max-w-md">
                    <Skull className="h-12 w-12 text-red-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-black italic uppercase tracking-tighter mb-2">Error de Sintonía</h2>
                    <p className="text-zinc-400 text-sm mb-6 uppercase tracking-wide">{error}</p>
                    <Button onClick={() => router.push("/")} className="bg-white text-black hover:bg-zinc-200 rounded-full px-8 font-black uppercase text-[10px] tracking-widest">
                        Volver al Inicio
                    </Button>
                </div>
            </div>
        );
    }

    // Rank Medal Logic
    const rankTier = player?.rank_tier;
    const rankFirstDigit = rankTier ? Math.floor(rankTier / 10) : 0;
    const rankStars = rankTier ? rankTier % 10 : 0;
    const rankIconUrl = `https://www.opendota.com/assets/images/dota2/rank_icons/rank_icon_${rankFirstDigit}.png`;
    const starIconUrl = `https://www.opendota.com/assets/images/dota2/rank_icons/rank_star_${rankStars}.png`;

    return (
        <main className="min-h-screen bg-[#020202] text-zinc-100 font-sans relative overflow-x-hidden">
            {/* Cinematic Background */}
            <div className="fixed inset-0 pointer-events-none z-0">
                <div
                    className="absolute inset-0 bg-cover bg-center brightness-[0.2] scale-105"
                    style={{ backgroundImage: "url('/player_bg.png')" }}
                />
                <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black" />
            </div>

            {/* Top Navigation */}
            <nav className="relative z-50 flex items-center justify-between px-6 md:px-12 py-3 backdrop-blur-md bg-black/40 border-b border-white/5">
                <div
                    className="flex items-center gap-3 cursor-pointer group"
                    onClick={() => router.push("/dashboard")}
                >
                    <div className="h-8 w-8 rounded-lg bg-zinc-900 border border-white/10 flex items-center justify-center group-hover:border-red-600/50 transition-colors">
                        <ChevronLeft className="h-4 w-4 text-zinc-400 group-hover:text-red-500" />
                    </div>
                    <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500 group-hover:text-zinc-200 transition-colors hidden sm:block">
                        Panel
                    </span>
                </div>

                <div className="flex items-center gap-4">
                    <Button
                        onClick={handleRefresh}
                        disabled={refreshing}
                        className="bg-red-600/10 border border-red-600/30 hover:bg-red-600 hover:text-white rounded-lg h-8 px-4 font-black uppercase text-[9px] tracking-widest text-red-500 transition-all shadow-[0_0_20px_rgba(220,38,38,0.1)]"
                    >
                        <Sparkles className={`mr-1.5 h-3 w-3 ${refreshing ? 'animate-spin' : ''}`} />
                        {refreshing ? "Sincronizando..." : "Actualizar"}
                    </Button>
                </div>
            </nav>

            <div className="relative z-10 max-w-6xl mx-auto px-6 py-2 md:py-4">

                {/* Ultra-Compact Profile Header Card */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-black/30 backdrop-blur-3xl border border-white/10 rounded-[1.5rem] p-3 md:p-5 mb-4 shadow-2xl relative overflow-hidden"
                >
                    <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
                        {/* Avatar & Medal Section */}
                        <div className="relative group shrink-0">
                            <div className="absolute -inset-1 bg-red-600/10 rounded-2xl blur transition-opacity" />
                            <div className="relative h-20 w-20 rounded-xl border border-white/10 overflow-hidden shadow-xl bg-black">
                                <img
                                    src={player?.avatar || "https://i.pravatar.cc/200"}
                                    alt={player?.personaname}
                                    className="h-full w-full object-cover"
                                />
                            </div>

                            {/* Medal Container - Floating Badge */}
                            <div className="absolute -bottom-2.5 -right-2.5 h-12 w-12 drop-shadow-[0_0_10px_rgba(0,0,0,0.9)]">
                                <img src={rankIconUrl} alt="Medal" className="h-full w-full object-contain" />
                                {rankTier && rankStars > 0 && rankFirstDigit < 8 && (
                                    <img src={starIconUrl} alt="Stars" className="absolute inset-0 h-full w-full object-contain" />
                                )}
                                {!rankTier && (
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <div className="bg-black/90 border border-white/10 px-1 py-0.5 rounded-sm">
                                            <span className="text-[6px] font-black text-zinc-500 uppercase tracking-tighter">OFF</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Text Info Section - Finer Spacing */}
                        <div className="flex-1 text-center md:text-left space-y-1.5 pt-0.5">
                            <div className="space-y-0.5">
                                <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-red-600/10 border border-red-600/20 text-red-500 text-[8px] font-black uppercase tracking-widest mb-0.5">
                                    <Shield className="h-2.5 w-2.5" /> {getRankName(player?.rank_tier || null)}
                                </div>
                                <h1 className="text-3xl md:text-6xl font-black italic uppercase tracking-tighter truncate max-w-[500px] leading-tight text-white">
                                    {player?.personaname}
                                </h1>
                            </div>

                            <div className="flex flex-wrap justify-center md:justify-start gap-4 items-center opacity-70">
                                <span className="text-zinc-500 font-bold uppercase text-[9px] tracking-[0.2em]">
                                    ID: <span className="text-zinc-300 ml-1">{player?.account_id}</span>
                                </span>
                                <div className="h-1 w-1 rounded-full bg-zinc-800" />
                                <span className="text-red-500 font-black uppercase text-[9px] tracking-[0.2em] flex items-center gap-2">
                                    <TrendingUp className="h-4 w-4" /> 54% Win Rate
                                    <span className="text-[8px] text-zinc-600 lowercase">(simulado)</span>
                                </span>
                            </div>

                            <div className="pt-1 flex flex-wrap justify-center md:justify-start gap-4">
                                <div className="flex items-center gap-2">
                                    <p className="text-[8px] font-black text-zinc-600 uppercase tracking-widest">Partidas:</p>
                                    <p className="text-sm font-black text-white italic">2,410</p>
                                </div>
                                <div className="h-3 w-px bg-white/10 self-center" />
                                <div className="flex items-center gap-2">
                                    <p className="text-[8px] font-black text-zinc-600 uppercase tracking-widest">Versatilidad:</p>
                                    <p className="text-sm font-black text-white italic">86%</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Warning Banner */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8 }}
                    className="mb-6 group flex items-start gap-4 p-4 bg-amber-950/5 border border-amber-600/10 rounded-xl hover:bg-amber-950/10 transition-all"
                >
                    <div className="h-8 w-8 rounded-lg bg-amber-600/10 border border-amber-600/20 flex items-center justify-center shrink-0">
                        <Info className="h-4 w-4 text-amber-500" />
                    </div>
                    <div className="space-y-0.5">
                        <p className="text-[9px] font-black uppercase tracking-widest text-amber-500 text-opacity-80">Oracle Protocol</p>
                        <p className="text-[10px] text-zinc-500 font-medium leading-relaxed">
                            Activa <span className="text-white">"Exponer datos de partidas públicas"</span> en el cliente para ver tus últimas batallas.
                        </p>
                    </div>
                </motion.div>

                {/* Match List Section */}
                <div className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="h-7 w-7 rounded-lg bg-red-600/10 border border-red-600/20 flex items-center justify-center">
                            <History className="h-3.5 w-3.5 text-red-500" />
                        </div>
                        <h2 className="text-lg font-black italic uppercase tracking-tighter">Registros de Batalla</h2>
                        <div className="h-px flex-1 bg-white/5" />
                    </div>

                    <div className="grid gap-2">
                        {matches.map((match, idx) => (
                            <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.05 * idx }}
                                key={match.match_id}
                                className="group relative bg-zinc-900/30 backdrop-blur-md border border-white/5 hover:border-red-600/30 rounded-xl p-3 transition-all flex flex-col md:flex-row items-center gap-5 cursor-pointer"
                                onClick={() => router.push(`/dashboard/${match.match_id}`)}
                            >
                                {/* Hero Card */}
                                <div className="flex items-center gap-4 min-w-[200px]">
                                    <div className="h-12 w-20 bg-zinc-950 rounded-lg border border-white/10 overflow-hidden relative shadow-lg">
                                        <div className={`absolute inset-0 bg-gradient-to-br opacity-40 ${match.result === 'Win' ? 'from-emerald-900/40' : 'from-red-900/40'}`} />
                                        <img
                                            src={`https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/${match.hero_img}.png`}
                                            alt={match.hero}
                                            className="h-full w-full object-cover group-hover:scale-110 transition-transform duration-500"
                                        />
                                    </div>
                                    <div>
                                        <h4 className="text-sm font-black italic uppercase tracking-tighter text-white">{match.hero}</h4>
                                        <div className={`text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded inline-block ${match.result === 'Win' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                                            {match.result === 'Win' ? 'VICTORIA' : 'DERROTA'}
                                        </div>
                                    </div>
                                </div>

                                {/* Stats Info */}
                                <div className="flex-1 grid grid-cols-3 gap-4 w-full border-t md:border-t-0 border-white/5 pt-2 md:pt-0">
                                    <div>
                                        <p className="text-[7px] font-black text-zinc-600 uppercase tracking-widest mb-0.5">KDA</p>
                                        <p className="text-xs font-black italic tracking-widest text-zinc-300">{match.kda}</p>
                                    </div>
                                    <div className="hidden sm:block">
                                        <p className="text-[7px] font-black text-zinc-600 uppercase tracking-widest mb-0.5">Duración</p>
                                        <p className="text-xs font-bold italic text-zinc-300 flex items-center gap-2">
                                            <Clock className="h-3 w-3 text-zinc-500" /> {match.duration}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-[7px] font-black text-zinc-600 uppercase tracking-widest mb-0.5">ID</p>
                                        <p className="text-[9px] font-mono text-zinc-600">#{match.match_id}</p>
                                    </div>
                                </div>

                                {/* Button */}
                                <Button
                                    className="w-full md:w-auto bg-white/5 hover:bg-white text-zinc-600 hover:text-black rounded-lg h-9 px-5 font-black uppercase text-[8px] tracking-widest border border-white/5 transition-all"
                                >
                                    Detalles <ChevronLeft className="ml-2 h-3 w-3 rotate-180" />
                                </Button>
                            </motion.div>
                        ))}
                        {matches.length === 0 && (
                            <div className="text-center py-16 bg-zinc-900/10 rounded-2xl border border-dashed border-white/5">
                                <History className="h-8 w-8 text-zinc-800 mx-auto mb-3" />
                                <p className="text-zinc-600 font-bold uppercase tracking-widest text-[10px]">Sin registros encontrados</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="relative z-10 p-8 text-center opacity-10 hover:opacity-100 transition-opacity">
                <p className="text-[8px] font-black text-zinc-500 uppercase tracking-[0.5em]">Oracle Protocol • Deep Analysis v2.0</p>
            </footer>
        </main>
    );
}
