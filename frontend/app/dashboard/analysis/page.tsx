"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Loader2, ArrowLeft, Trophy, Clock, AlertTriangle, Activity, Zap, Coins, Map as MapIcon, Users, Eye, Sparkles } from "lucide-react";
import Link from "next/link";
import axios from "axios";
import { API_BASE } from "@/lib/api";
import ChatInterface from "@/components/ChatInterface";
import HeroList from "@/components/HeroList";
import NetWorthChart from "@/components/NetWorthChart";
import LaneMap from "@/components/LaneMap";
import MatchStats from "@/components/MatchStats";
import LoadingScreen from "@/components/ui/LoadingScreen";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

function MatchAnalysisContent() {
    const searchParams = useSearchParams();
    const matchId = searchParams.get('matchId');
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentMin, setCurrentMin] = useState<number>(-1);
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        if (loading) {
            const timer = setInterval(() => {
                setProgress((oldProgress) => {
                    const diff = Math.random() * 10;
                    return Math.min(oldProgress + diff, 98);
                });
            }, 300);
            return () => clearInterval(timer);
        } else {
            setProgress(100);
        }
    }, [loading]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const res = await axios.get(`${API_BASE}/match/${matchId}`);
                setData(res.data);
            } catch (err: any) {
                setError(err.response?.data?.detail || "Error de conexión. Asegúrate que el backend esté corriendo.");
            } finally {
                setLoading(false);
            }
        };
        if (matchId) fetchData();
    }, [matchId]);

    if (!matchId) return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center text-red-500 gap-4">
            <h1 className="text-xl font-bold uppercase tracking-widest">No se proporcionó un ID de partida.</h1>
            <Link href="/"><button className="px-6 py-2 bg-red-900/20 border border-red-900/50 rounded hover:bg-red-900/40 transition">Retorno a Base</button></Link>
        </div>
    );

    if (loading || progress < 100) return <LoadingScreen progress={Math.round(progress)} />;

    if (error || !data) return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center text-red-500 gap-4">
            <AlertTriangle className="w-16 h-16 opacity-50" />
            <h1 className="text-xl font-bold uppercase tracking-widest">{error || "Error Desconocido"}</h1>
            <Link href="/"><button className="px-6 py-2 bg-red-900/20 border border-red-900/50 rounded hover:bg-red-900/40 transition">Retorno a Base</button></Link>
        </div>
    );

    const { metadata, players } = data;

    return (
        <div className="min-h-screen bg-[#050508] text-zinc-100 font-sans pb-10 relative">
            <div className="fixed inset-0 pointer-events-none z-0">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_#1a1a2e_0%,_#000000_100%)] opacity-40" />
                <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-blue-900/10 to-transparent opacity-30" />
            </div>

            <header className="relative z-10 border-b border-white/5 bg-black/40 backdrop-blur-xl sticky top-0">
                <div className="max-w-[1920px] mx-auto px-4 md:px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-6">
                        <Link href="/">
                            <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition cursor-pointer border border-white/5">
                                <ArrowLeft size={18} className="text-zinc-400" />
                            </div>
                        </Link>
                        <div>
                            <div className="flex items-center gap-4">
                                <h1 className="text-xl md:text-2xl font-black italic uppercase tracking-tighter text-white flex items-center gap-2">
                                    MATCH {matchId}
                                </h1>
                                {metadata.partial_data && (
                                    <div className="flex items-center gap-2 px-3 py-1 bg-amber-500/10 border border-amber-500/30 rounded-full text-amber-500 animate-pulse">
                                        <AlertTriangle size={12} />
                                        <span className="text-[10px] font-black uppercase tracking-widest">Sincronización Parcial</span>
                                    </div>
                                )}
                                <button
                                    onClick={() => window.location.reload()}
                                    className="p-2 rounded-full bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white transition-all border border-white/5"
                                    title="Actualizar Datos"
                                >
                                    <Activity size={16} />
                                </button>
                            </div>
                            <div className="flex items-center gap-4 text-[10px] font-bold text-zinc-500 uppercase tracking-widest mt-1">
                                <span className="flex items-center gap-1"><Clock size={10} /> {metadata.duration_minutes} MIN</span>
                                <span className="flex items-center gap-1 text-zinc-600">|</span>
                                <span className="flex items-center gap-1"><MapIcon size={10} /> RANKED</span>
                            </div>
                        </div>
                    </div>

                    <div className="hidden md:flex items-center gap-8 bg-black/40 px-8 py-2 rounded-xl border border-white/5 shadow-2xl">
                        <div className="text-right">
                            <div className="text-[10px] font-black text-emerald-500 tracking-[0.2em] mb-1">RADIANT</div>
                            <div className="text-3xl font-black leading-none text-emerald-100">{metadata.radiant_score}</div>
                        </div>
                        <div className="text-zinc-700 font-black text-xl italic opacity-50">VS</div>
                        <div className="text-left">
                            <div className="text-[10px] font-black text-rose-500 tracking-[0.2em] mb-1">DIRE</div>
                            <div className="text-3xl font-black leading-none text-rose-100">{metadata.dire_score}</div>
                        </div>
                    </div>
                </div>
            </header>

            <main className="relative z-10 max-w-[1920px] mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                <section className="col-span-1 lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-[#0c0c10]/80 backdrop-blur-sm border border-white/5 rounded-2xl overflow-hidden shadow-2xl flex flex-col max-h-[70vh]">
                        <div className="p-4 border-b border-teal-500/20 bg-teal-500/5 flex items-center justify-between">
                            <span className="text-[10px] font-black uppercase text-teal-400 flex items-center gap-2 tracking-[0.2em]">
                                <Users size={12} /> Inteligencia de Batalla
                            </span>
                        </div>
                        <div className="overflow-y-auto scrollbar-hide p-4 space-y-6">
                            <HeroList players={players} teamFilter="Radiant" />
                            <div className="h-px bg-white/5 my-4" />
                            <HeroList players={players} teamFilter="Dire" />
                        </div>
                    </div>
                    <div className="bg-[#0c0c10] border border-white/5 rounded-2xl p-6 shadow-xl">
                        <div className="flex items-center gap-2 mb-4">
                            <Activity className="w-4 h-4 text-zinc-500" />
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">Ventaja de Oro</span>
                        </div>
                        <div className="h-[200px]">
                            <NetWorthChart goldAdvantage={metadata.gold_advantage} />
                        </div>
                    </div>
                </section>

                <section className="col-span-1 lg:col-span-5 flex flex-col gap-6">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="relative bg-[#0c0c10]/40 border border-teal-500/20 rounded-[2.5rem] p-8 overflow-hidden group cursor-pointer hover:border-teal-500/50 transition-all duration-700 shadow-[0_0_50px_rgba(20,184,166,0.1)]"
                        onClick={() => setIsChatOpen(true)}
                    >
                        <div className="absolute inset-0 bg-gradient-to-b from-teal-500/5 to-transparent opacity-50" />
                        <div className="relative z-10 flex flex-col items-center text-center space-y-6">
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-[9px] font-black uppercase tracking-[0.3em]">
                                <Sparkles size={10} className="animate-pulse" /> Oracle Intelligence Ready
                            </div>
                            <div className="relative">
                                <div className="absolute inset-0 bg-teal-500 blur-[40px] opacity-20 group-hover:opacity-40 animate-pulse transition-opacity" />
                                <div className="w-24 h-24 rounded-full bg-black/60 border-2 border-teal-500/30 flex items-center justify-center relative z-10 group-hover:scale-110 group-hover:border-teal-400 transition-all duration-500 shadow-2xl">
                                    <Eye size={48} className="text-teal-400 group-hover:text-white transition-colors" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <h2 className="text-2xl font-black italic uppercase tracking-tighter text-white">
                                    Consultar al <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-white">Oráculo</span>
                                </h2>
                                <p className="text-zinc-500 text-xs font-medium max-w-sm mx-auto leading-relaxed">
                                    Haz clic para iniciar el análisis profundo de los hilos del destino de esta batalla.
                                </p>
                            </div>
                            <Button className="bg-teal-600 hover:bg-teal-500 text-white font-black uppercase tracking-widest text-[10px] h-10 px-8 rounded-full shadow-[0_0_20px_rgba(20,184,166,0.3)] transition-all">
                                Iniciar Chat de Guerra
                            </Button>
                        </div>
                    </motion.div>

                    <div className="flex items-center gap-4 mb-2 opacity-60">
                        <div className="h-px flex-1 bg-gradient-to-r from-transparent to-teal-500/30" />
                        <span className="text-[10px] font-black uppercase tracking-[0.4em] text-white">Registros de Batalla</span>
                        <div className="h-px flex-1 bg-gradient-to-l from-transparent to-teal-500/30" />
                    </div>

                    <div className="grid grid-cols-1 gap-4">
                        <MatchStats players={players} metadata={metadata} />
                    </div>
                </section>

                <section className="col-span-1 lg:col-span-3">
                    <div className="bg-[#0c0c10] border border-white/5 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
                        <div className="p-4 border-b border-white/5 bg-black/20 flex items-center justify-between">
                            <span className="text-[10px] font-black uppercase text-zinc-400 flex items-center gap-2 tracking-widest">
                                <MapIcon size={12} /> Tactical Map
                            </span>
                        </div>
                        <div className="p-2 bg-zinc-950/50">
                            <div className="aspect-square">
                                <LaneMap players={players} currentTime={currentMin} partialData={metadata.partial_data} />
                            </div>
                        </div>
                        <div className="p-4 bg-black/60 border-t border-white/5">
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-[9px] uppercase font-black text-zinc-600 tracking-[0.2em]">Temporal Nexus</span>
                                <span className="text-[10px] font-mono font-black text-blue-400">
                                    {currentMin < 0 ? "START" : `MIN: ${currentMin}`}
                                </span>
                            </div>
                            <input
                                type="range"
                                min="-1"
                                max={metadata.duration_minutes}
                                value={currentMin}
                                onChange={(e) => setCurrentMin(parseInt(e.target.value))}
                                className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-teal-600"
                            />
                        </div>
                    </div>
                </section>
            </main>

            <ChatInterface
                matchId={matchId}
                isOpen={isChatOpen}
                onToggle={() => setIsChatOpen(!isChatOpen)}
                hideButton={true}
            />
        </div>
    );
}

export default function MatchAnalysis() {
    return (
        <Suspense fallback={<LoadingScreen progress={10} />}>
            <MatchAnalysisContent />
        </Suspense>
    );
}
