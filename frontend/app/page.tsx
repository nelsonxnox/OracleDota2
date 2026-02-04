"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Sparkles, Search, History, Shield, Info, Swords, ArrowRight, Lock, LogOut } from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { auth } from "@/lib/firebase";
import { signOut } from "firebase/auth";
import LoadingScreen from "@/components/ui/LoadingScreen";
import AuthModal from "@/components/AuthModal";
import { User as UserIcon } from "lucide-react";

export default function Home() {
  const [searchId, setSearchId] = useState("");
  const router = useRouter();
  const { user, loading } = useAuth();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const handleSearch = () => {
    if (!searchId) return;
    router.push(`/dashboard/${searchId}`);
  };

  const handleLogout = async () => {
    await signOut(auth);
  };

  if (loading) return <LoadingScreen progress={50} />;

  return (
    <main className="min-h-screen bg-black text-zinc-100 flex flex-col selection:bg-red-500/30 font-sans overflow-x-hidden">
      {/* Cinematic Background Layer */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center brightness-[0.25] scale-105 animate-[slow-zoom_40s_linear_infinite]"
          style={{ backgroundImage: "url('/dota2_oracle_bg.png')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-black/80" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,_rgba(168,85,247,0.1)_0%,_transparent_70%)]" />
      </div>

      {/* Navigation Bar */}
      <nav className="relative z-50 flex items-center justify-between px-6 md:px-12 py-6 border-b border-white/5 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-red-600 to-red-900 flex items-center justify-center shadow-[0_0_20px_rgba(220,38,38,0.3)]">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-black tracking-tighter uppercase italic text-white">
            Oracle<span className="text-red-500">Dota</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          {!loading && (
            user ? (
              <div className="flex items-center gap-4">
                <Link href="/dashboard">
                  <Button variant="ghost" className="text-zinc-400 hover:text-white hover:bg-white/5 font-bold uppercase tracking-widest text-[10px]">
                    Ir al Panel de Guerra
                  </Button>
                </Link>
                <div
                  onClick={() => router.push("/dashboard")}
                  className="flex items-center gap-3 bg-white/5 p-1 pr-4 rounded-full border border-white/10 hover:bg-white/10 cursor-pointer transition-all"
                >
                  <div className="h-7 w-7 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 flex items-center justify-center border border-white/10">
                    <UserIcon className="h-3 w-3 text-zinc-400" />
                  </div>
                  <span className="text-[10px] font-black text-white uppercase tracking-widest">Mi Cuenta</span>
                </div>
                <Button onClick={handleLogout} variant="ghost" className="text-red-500 hover:text-red-400 hover:bg-red-500/5 font-bold uppercase tracking-widest text-[10px] px-2 h-8">
                  <LogOut className="h-3.5 w-3.5" />
                </Button>
              </div>
            ) : (
              <>
                <Button
                  onClick={() => setIsAuthModalOpen(true)}
                  variant="ghost"
                  className="text-zinc-400 hover:text-white hover:bg-white/5 font-bold uppercase tracking-widest text-[10px]"
                >
                  Panel de Cuenta
                </Button>
                <Button
                  onClick={() => setIsAuthModalOpen(true)}
                  className="bg-white text-black hover:bg-zinc-200 font-black uppercase tracking-widest text-[10px] px-6 h-9 rounded-full shadow-[0_0_15px_rgba(255,255,255,0.2)]"
                >
                  Registrarse
                </Button>
              </>
            )
          )}
        </div>
      </nav>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />

      {/* Hero Section */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center p-6 text-center max-w-6xl mx-auto w-full mt-10 md:mt-0">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="space-y-8 mb-16"
        >

          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-red-600/10 border border-red-600/20 text-red-500 text-[10px] font-black uppercase tracking-[0.2em] shadow-[0_0_20px_rgba(220,38,38,0.1)] mb-4">
            <Shield className="h-3 w-3" />
            AI Powered Coach
          </div>

          <h1 className="text-5xl md:text-8xl font-black tracking-tighter italic uppercase leading-[0.9]">
            Domina el <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-red-200 to-zinc-400 drop-shadow-[0_0_30px_rgba(220,38,38,0.2)]">
              Campo de Batalla
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-zinc-400 text-sm md:text-lg font-medium leading-relaxed tracking-wide opacity-90">
            Tu coach personal impulsado por Inteligencia Artificial. Analizamos tus partidas, detectamos errores y te guiamos hacia la victoria con precisión milimétrica.
          </p>
        </motion.div>

        {/* Interactive Demo Section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          className="w-full max-w-4xl grid md:grid-cols-5 gap-4"
        >

          {/* Demo Input (Match ID) - Takes up left side */}
          <div className="md:col-span-3 bg-zinc-900/80 backdrop-blur-2xl border border-white/10 rounded-2xl p-1 shadow-2xl relative group overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-red-600 to-transparent opacity-50 group-hover:opacity-100 transition-opacity"></div>

            <div className="bg-black/40 rounded-xl p-6 flex flex-col gap-4 h-full justify-center">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-zinc-300">
                  <Swords className="h-4 w-4 text-red-500" />
                  <span className="text-xs font-black uppercase tracking-widest">Prueba el Coach</span>
                </div>
                <span className="text-[10px] text-zinc-500 uppercase font-bold bg-zinc-900 px-2 py-1 rounded">Demo Gratuita</span>
              </div>

              <div className="relative">
                <Input
                  placeholder="INGRESA MATCH ID (EJ: 7560636884)"
                  value={searchId}
                  onChange={(e) => setSearchId(e.target.value)}
                  className="h-14 pl-4 pr-14 bg-zinc-950/50 border-zinc-800 text-lg font-bold italic tracking-wider placeholder:text-zinc-700/50 focus-visible:ring-1 focus-visible:ring-red-900 text-white"
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button
                  onClick={handleSearch}
                  disabled={!searchId}
                  size="icon"
                  className="absolute right-1 top-1 h-12 w-12 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all"
                >
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </div>
              <p className="text-[10px] text-zinc-500 text-left pl-1">
                *Analiza una partida individual para ver el poder de Oracle.
              </p>
            </div>
          </div>

          {/* Locked Feature (Profile Analysis) - Takes up right side */}
          <div className="md:col-span-2 bg-zinc-900/40 backdrop-blur-sm border border-white/5 rounded-2xl p-6 relative overflow-hidden group cursor-pointer hover:bg-zinc-900/60 transition-all flex flex-col justify-center items-center text-center">
            <div className="absolute inset-0 bg-[url('/grid-pattern.png')] opacity-5"></div>

            <div className="h-12 w-12 rounded-full bg-zinc-800 flex items-center justify-center mb-4 group-hover:bg-teal-900/30 group-hover:text-teal-400 transition-all">
              <Lock className="h-5 w-5 text-zinc-500 group-hover:text-teal-400" />
            </div>

            <h3 className="text-sm font-black uppercase tracking-widest text-zinc-300 mb-2">Análisis de Perfil</h3>
            <p className="text-xs text-zinc-500 leading-relaxed mb-4">
              {user ? "Ya tienes acceso al análisis completo de tu cuenta." : "Desbloquea el análisis completo de tu cuenta, historial y evolución registrándote."}
            </p>

            <Link href={user ? "/dashboard" : "/register"} className="w-full">
              <Button variant="outline" className="w-full border-zinc-700 hover:border-teal-500 hover:text-teal-400 bg-transparent text-[10px] font-bold uppercase tracking-widest h-8">
                {user ? "Ver mi Perfil" : "Crear Cuenta"}
              </Button>
            </Link>
          </div>

        </motion.div>

        {/* Feature Highlights (Icons) */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 px-4 opacity-60"
        >
          {[
            { label: 'Visión Computacional', desc: 'Análisis de Wards', icon: Search },
            { label: 'Machine Learning', desc: 'Predicción de Winrate', icon: Sparkles },
            { label: 'Builds Dinámicas', desc: 'Adaptación en Tiempo Real', icon: Shield },
            { label: 'Análisis de Replay', desc: 'Errores al micro-segundo', icon: History }
          ].map((feature, i) => (
            <div key={i} className="flex flex-col items-center gap-3 text-zinc-500 hover:text-zinc-300 transition-colors">
              <div className="p-3 rounded-full bg-white/5 border border-white/5">
                <feature.icon className="h-5 w-5" />
              </div>
              <div>
                <span className="block text-[10px] font-black uppercase tracking-widest mb-1">{feature.label}</span>
                <span className="block text-[9px] font-medium tracking-wide opacity-70">{feature.desc}</span>
              </div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Modern Footer with Signature */}
      <footer className="relative z-50 py-8 border-t border-white/5 bg-black/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">

          <div className="flex flex-col items-center md:items-start gap-1">
            <p className="text-[10px] uppercase tracking-[0.3em] text-zinc-500 font-black">
              © {new Date().getFullYear()} Nelson Planes Arencibia
            </p>
            <p className="text-[9px] text-zinc-700 font-bold uppercase tracking-widest">
              Todos los derechos reservados
            </p>
          </div>

          <div className="flex gap-8">
            {['Privacidad', 'Términos', 'Contacto'].map(item => (
              <a key={item} href="#" className="text-[10px] font-bold uppercase tracking-widest text-zinc-600 hover:text-white transition-colors">{item}</a>
            ))}
          </div>

          <div className="opacity-30 grayscale hover:grayscale-0 transition-all duration-500">
            <Sparkles className="h-6 w-6 text-zinc-600" />
          </div>
        </div>
      </footer>

      <style jsx global>{`
        @keyframes slow-zoom {
          0% { transform: scale(1); }
          50% { transform: scale(1.1); }
          100% { transform: scale(1); }
        }
      `}</style>
    </main>
  );
}
