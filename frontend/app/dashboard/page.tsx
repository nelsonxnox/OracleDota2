"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Swords, Search, User as UserIcon, Gamepad2, Sparkles, LogOut, History, TrendingUp, Copy, Check, Key, AlertCircle, Zap } from "lucide-react";
import { motion } from "framer-motion";
import { auth } from "@/lib/firebase";
import { signOut } from "firebase/auth";
import LoadingScreen from "@/components/ui/LoadingScreen";
import LiveCoachCard from "@/components/LiveCoachCard";
import LiveTokenCard from "@/components/LiveTokenCard";
import PlansPanel from "@/components/PlansPanel";
import PlayerStatsCard from "@/components/PlayerStatsCard";

export default function DashboardPage() {
    const { user, userData, loading } = useAuth();
    const router = useRouter();
    const [searchId, setSearchId] = useState("");
    const [progress, setProgress] = useState(0);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        if (loading) {
            const timer = setInterval(() => {
                setProgress(p => Math.min(p + Math.random() * 15, 95));
            }, 300);
            return () => clearInterval(timer);
        } else {
            setProgress(100);
        }
    }, [loading]);

    useEffect(() => {
        if (!loading && !user) {
            router.push("/login");
        }
    }, [user, loading, router]);

    const handleSearch = () => {
        if (searchId) {
            router.push(`/dashboard/analysis?matchId=${searchId}`);
        }
    };

    const handleLogout = async () => {
        await signOut(auth);
        router.push("/");
    };

    const copyToClipboard = () => {
        if (user?.uid) {
            navigator.clipboard.writeText(user.uid);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    if (loading || progress < 100) return <LoadingScreen progress={Math.round(progress)} />;

    return (
        <main className="min-h-screen bg-black text-zinc-100 relative overflow-hidden font-sans">
            {/* Cinematic Background */}
            <div className="fixed inset-0 pointer-events-none">
                <div
                    className="absolute inset-0 bg-cover bg-center brightness-[0.3] scale-105"
                    style={{ backgroundImage: "url('/dashboard_bg.png')" }}
                />
                <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-transparent to-black" />
                <div className="absolute inset-0 bg-gradient-to-b from-black/90 via-transparent to-black/90" />
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_rgba(220,38,38,0.1)_0%,_transparent_100%)]" />
            </div>

            {/* Navigation Bar */}
            <nav className="relative z-50 flex items-center justify-between px-6 md:px-12 py-6 border-b border-white/5 backdrop-blur-md bg-black/40 sticky top-0">
                <div className="flex items-center gap-3 cursor-pointer" onClick={() => router.push("/")}>
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-red-600 to-red-900 flex items-center justify-center shadow-[0_0_20px_rgba(220,38,38,0.3)]">
                        <Sparkles className="h-5 w-5 text-white" />
                    </div>
                    <span className="text-xl font-black tracking-tighter uppercase italic text-white hidden md:block">
                        Oracle<span className="text-red-500">Dota</span>
                    </span>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-3 bg-zinc-900/80 p-1.5 pl-4 rounded-full border border-white/10 backdrop-blur-xl hover:bg-zinc-800 transition-colors cursor-pointer" onClick={() => router.push("/profile")}>
                        <div className="flex flex-col items-end mr-1 hidden sm:flex">
                            <span className="text-[10px] font-black text-zinc-500 uppercase leading-none mb-1">Comandante</span>
                            <span className="text-xs font-bold text-white leading-none">{user?.email?.split('@')[0]}</span>
                        </div>
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 flex items-center justify-center border border-white/10 ring-2 ring-transparent group-hover:ring-red-500/50 transition-all">
                            <UserIcon className="h-4 w-4 text-zinc-400 group-hover:text-white" />
                        </div>
                    </div>
                    <Button
                        onClick={handleLogout}
                        size="icon"
                        variant="ghost"
                        className="h-10 w-10 rounded-full text-zinc-500 hover:text-red-500 hover:bg-red-500/10 transition-colors"
                    >
                        <LogOut className="h-5 w-5" />
                    </Button>
                </div>
            </nav>

            <div className="relative z-10 max-w-6xl mx-auto p-6 md:p-12 space-y-12">

                {/* Header Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4 text-center md:text-left flex flex-col md:flex-row justify-between items-end gap-6"
                >
                    <div className="space-y-2">
                        <h1 className="text-4xl md:text-6xl font-black italic uppercase tracking-tighter drop-shadow-2xl">
                            Tu Panel de <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-red-800 animate-pulse">Guerra</span>
                        </h1>
                        <p className="text-zinc-400 font-medium tracking-wide max-w-xl">Analiza tus batallas, descubre tus errores y asciende hacia la inmortalidad con el poder del Oráculo.</p>
                    </div>
                </motion.div>

                {/* ORACLE PROTOCOL BANNER (NEW) */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="relative overflow-hidden rounded-[2rem] bg-gradient-to-r from-orange-600/10 via-red-600/10 to-transparent border border-orange-500/30 p-1"
                >
                    <div className="absolute inset-0 bg-[url('/noise.png')] opacity-20 mix-blend-overlay" />
                    <div className="relative bg-black/40 backdrop-blur-xl rounded-[1.8rem] p-6 md:p-8 flex flex-col md:flex-row items-center gap-6">
                        <div className="h-16 w-16 md:h-20 md:w-20 rounded-full bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center shadow-[0_0_40px_rgba(234,88,12,0.4)] animate-pulse">
                            <AlertCircle className="h-8 w-8 md:h-10 md:w-10 text-white" />
                        </div>
                        <div className="flex-1 text-center md:text-left space-y-2">
                            <h3 className="text-2xl md:text-3xl font-black uppercase italic tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-500">
                                ⚡ Oracle Protocol: Activación Requerida
                            </h3>
                            <p className="text-zinc-300 font-medium text-sm md:text-base max-w-3xl">
                                Para que el Oráculo pueda analizar tu historial completo, debes activar la opción <span className="text-white font-bold bg-white/10 px-2 py-0.5 rounded border border-white/10">"Exponer datos de partidas públicas"</span> en la configuración de Dota 2. Sin esto, tu destino permanecerá oculto.
                            </p>
                        </div>
                        <Button
                            variant="outline"
                            className="border-orange-500/50 text-orange-400 hover:bg-orange-500/10 font-bold uppercase tracking-wider"
                            onClick={() => window.open('https://www.dota2.com', '_blank')}
                        >
                            Ver Guía
                        </Button>
                    </div>
                </motion.div>

                <div className="grid md:grid-cols-2 gap-8">

                    {/* User Profile Card */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="group bg-zinc-900/40 backdrop-blur-2xl border border-white/10 rounded-[2.5rem] p-8 md:p-10 space-y-8 relative overflow-hidden hover:bg-zinc-900/60 transition-all duration-500"
                    >
                        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                            <History className="h-32 w-32" />
                        </div>

                        <div className="space-y-6">
                            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-2xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
                                <Gamepad2 className="h-5 w-5" />
                                <span className="text-xs font-black uppercase tracking-widest">Tu Legado en Oracle</span>
                            </div>

                            <div className="space-y-2">
                                <h3 className="text-2xl font-black uppercase italic tracking-tighter">Mi Perfil Inmortal</h3>
                                <p className="text-zinc-400 text-sm leading-relaxed">
                                    Accede a tus estadísticas personalizadas, historial de partidas y recomendaciones del Oráculo basadas en tu desempeño real.
                                </p>
                            </div>

                            {userData?.dota_id ? (
                                <div className="space-y-6 pt-4">
                                    <div className="bg-black/40 border border-white/5 rounded-2xl p-6 relative overflow-hidden">
                                        <div className="absolute top-0 right-0 p-2 opacity-10">
                                            <Sparkles className="h-24 w-24 text-teal-500" />
                                        </div>

                                        <div className="flex flex-col items-center justify-center space-y-2 relative z-10">
                                            <span className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.2em]">Dota Friend ID</span>
                                            <div className="text-4xl font-black tracking-[0.2em] text-white tabular-nums">
                                                {userData.dota_id}
                                            </div>
                                        </div>

                                        {/* NEW: REAL STATS FROM OPENDOTA */}
                                        <PlayerStatsCard accountId={userData.dota_id} />
                                    </div>

                                    <Button
                                        onClick={() => router.push(`/player?id=${userData.dota_id}`)}
                                        className="w-full bg-gradient-to-r from-teal-600 to-teal-800 hover:from-teal-500 hover:to-teal-700 text-white font-black uppercase tracking-widest py-8 rounded-2xl shadow-[0_0_30px_rgba(20,184,166,0.2)] group transition-all hover:scale-[1.02]"
                                    >
                                        Explorar Mi Historial <TrendingUp className="ml-2 h-5 w-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                                    </Button>
                                </div>
                            ) : (
                                <div className="space-y-6 pt-4 text-center">
                                    <p className="text-zinc-500 text-xs italic bg-zinc-950/50 p-4 rounded-xl border border-white/5">
                                        ⚠️ Aún no has vinculado tu Friend ID. Hazlo para desbloquear el análisis de perfil.
                                    </p>
                                    <Button className="w-full border border-teal-500/30 hover:border-teal-400 text-teal-500 hover:bg-teal-500/5 bg-transparent font-black uppercase tracking-widest py-8 rounded-2xl transition-all">
                                        Vincular Cuenta Ahora
                                    </Button>
                                </div>
                            )}
                        </div>
                    </motion.div>

                    {/* Quick Match ID Analysis Card */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="group bg-zinc-900/40 backdrop-blur-2xl border border-white/10 rounded-[2.5rem] p-8 md:p-10 space-y-8 relative overflow-hidden hover:bg-zinc-900/60 transition-all duration-500"
                    >
                        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Swords className="h-32 w-32" />
                        </div>

                        <div className="space-y-6">
                            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500">
                                <Search className="h-5 w-5" />
                                <span className="text-xs font-black uppercase tracking-widest">Analizador de Batallas</span>
                            </div>

                            <div className="space-y-2">
                                <h3 className="text-2xl font-black uppercase italic tracking-tighter">Entrada Instantánea</h3>
                                <p className="text-zinc-400 text-sm leading-relaxed">
                                    Ingresa el ID de cualquier partida (<span className="text-zinc-300">tuya, de amigos o de profesionales</span>) y deja que Oracle revele la verdad oculta tras el resultado. ⚔️
                                </p>
                            </div>

                            <div className="space-y-6 pt-4">
                                <div className="relative group/input">
                                    <div className="absolute -inset-1 bg-gradient-to-r from-red-600 to-purple-600 rounded-2xl blur opacity-20 group-focus-within/input:opacity-50 transition-opacity duration-500" />
                                    <div className="relative">
                                        <Input
                                            placeholder="PEGA EL MATCH ID AQUÍ..."
                                            value={searchId}
                                            onChange={(e) => setSearchId(e.target.value)}
                                            className="bg-black/60 border-white/10 h-16 pl-6 pr-20 font-black italic tracking-widest text-lg placeholder:text-zinc-700 focus-visible:ring-offset-0 focus-visible:ring-1 focus-visible:ring-red-500/50 rounded-2xl transition-all"
                                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                        />
                                        <Button
                                            onClick={handleSearch}
                                            disabled={!searchId}
                                            className="absolute right-2 top-2 bottom-2 w-12 bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-lg transition-all"
                                        >
                                            <Search className="h-5 w-5" />
                                        </Button>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 px-2">
                                    <div className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
                                    <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest">
                                        Oracle Engine: Online & Deep Mode Ready
                                    </p>
                                </div>
                            </div>
                        </div>
                    </motion.div>

                </div>

                {/* NEW SECTION: Oracle Live Coach */}
                <div className="max-w-4xl mx-auto space-y-8">
                    <LiveTokenCard />
                    <LiveCoachCard />
                </div>

                {/* PLANS PANEL SECTION */}
                <section className="pt-12 border-t border-white/5">
                    <PlansPanel />
                </section>

                {/* Optional: Footer or Extra Stats */}
                <div className="pt-12 flex flex-col items-center justify-center opacity-30">
                    <div className="h-px w-24 bg-gradient-to-r from-transparent via-zinc-500 to-transparent mb-6" />
                    <p className="text-[10px] font-black uppercase tracking-[0.5em] text-zinc-700">Explorando el Plano Astral</p>
                </div>
            </div>
        </main>
    );
}
