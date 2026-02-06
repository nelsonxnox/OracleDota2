"use client";

import { motion } from "framer-motion";
import { Mic, Zap, Brain, ArrowDownCircle, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LiveCoachCard() {
    const handleDownload = () => {
        // Production backend URL
        window.location.href = "https://oracledota2.onrender.com/download/OracleNeuralLink.exe";
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="group relative overflow-hidden rounded-[2.5rem] border border-orange-500/20 bg-zinc-900/40 backdrop-blur-2xl p-8 md:p-10 transition-all duration-500 hover:bg-zinc-900/60"
        >
            {/* Background Effects */}
            <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-orange-500/5 blur-3xl group-hover:bg-orange-500/10 transition-all duration-500" />
            <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <div className="relative space-y-8">
                {/* Header Badge */}
                <div className="flex items-center justify-between">
                    <div className="inline-flex items-center gap-3 rounded-2xl border border-orange-500/20 bg-orange-500/10 px-4 py-2 text-orange-500">
                        <Activity className="h-5 w-5 animate-pulse" />
                        <span className="text-xs font-black uppercase tracking-widest">Neural Link Activo</span>
                    </div>
                </div>

                {/* Content */}
                <div className="space-y-4">
                    <div className="flex items-center gap-4">
                        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500 to-red-600 shadow-lg shadow-orange-500/20">
                            <Brain className="h-8 w-8 text-white" />
                        </div>
                        <div>
                            <h3 className="text-3xl font-black italic tracking-tighter text-white uppercase">
                                Oracle <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-500">Live</span>
                            </h3>
                            <p className="text-xs font-bold uppercase tracking-widest text-zinc-500">
                                Asistente Táctico v1.0
                            </p>
                        </div>
                    </div>

                    <p className="max-w-md text-sm leading-relaxed text-zinc-400">
                        Conecta el cerebro de Oracle directamente a tu partida. Recibe análisis de voz en tiempo real, alertas de economía y predicciones tácticas.
                    </p>

                    {/* Feature Grid */}
                    <div className="grid grid-cols-2 gap-4 py-2">
                        <div className="flex items-center gap-3 rounded-xl bg-black/40 p-3 border border-white/5">
                            <Mic className="h-5 w-5 text-orange-400" />
                            <span className="text-xs font-bold text-zinc-300">Interacción de Voz</span>
                        </div>
                        <div className="flex items-center gap-3 rounded-xl bg-black/40 p-3 border border-white/5">
                            <Zap className="h-5 w-5 text-yellow-400" />
                            <span className="text-xs font-bold text-zinc-300">Alertas al Instante</span>
                        </div>
                    </div>
                </div>

                {/* Action Button */}
                <Button
                    onClick={handleDownload}
                    className="w-full bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white font-black uppercase tracking-widest py-8 rounded-2xl shadow-[0_0_30px_rgba(249,115,22,0.2)] group transition-all"
                >
                    <ArrowDownCircle className="mr-2 h-6 w-6 group-hover:translate-y-1 transition-transform" />
                    Descargar Neural Link
                </Button>

                <p className="text-center text-[10px] uppercase tracking-widest text-zinc-600">
                    Solo para Windows 10/11 • No requiere instalación
                </p>
            </div>
        </motion.div>
    );
}
