"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Zap, ShieldAlert, BrainCircuit } from "lucide-react";

const APP_QUOTES = [
    "Analizando los hilos del destino en el carril superior...",
    "Invocando al Oráculo para procesar los datos de la partida...",
    "Calculando la eficiencia de tus wards (o la falta de ellos)...",
    "Revisando por qué tu Carry no tiene BKB al minuto 30...",
    "El Oráculo está consultando las runas de recompensa...",
    "Desentrañando los secretos de tu última derrota...",
    "Mapeando la visión del mapa. El enemigo está cerca...",
];

const EPIC_QUOTES = [
    "¡La batalla por el Ancestro ha comenzado!",
    "El destino es un río, y yo soy el puente.",
    "Las estrellas nos guían hacia la victoria o la ruina.",
    "La victoria favorece a los preparados.",
    "Un héroe se levanta, una leyenda cae.",
];

const SARCASTIC_QUOTES = [
    "Recalculando tu MMR (intentando no reír)...",
    "Buscando el botón de 'Reportar' preventivamente...",
    "Cargando más rápido que un Pudge con Botas de Viaje.",
    "Analizando por qué perdiste por culpa de 'ese' compañero...",
    "Inyectando 500 unidades de paciencia en tu sistema...",
    "Esperando a que el soporte compre un ward. Esto puede tardar...",
];

export default function LoadingScreen({ progress = 0 }: { progress?: number }) {
    const [quote1, setQuote1] = useState("");
    const [quote2, setQuote2] = useState("");
    const [bgIndex, setBgIndex] = useState(1);

    useEffect(() => {
        // Select random background and quotes
        setBgIndex(Math.random() > 0.5 ? 1 : 2);
        setQuote1(APP_QUOTES[Math.floor(Math.random() * APP_QUOTES.length)]);

        // Mix Epic and Sarcastic for the second quote
        const mix = [...EPIC_QUOTES, ...SARCASTIC_QUOTES];
        setQuote2(mix[Math.floor(Math.random() * mix.length)]);
    }, []);

    return (
        <div className="fixed inset-0 z-[1000] flex items-center justify-center overflow-hidden bg-black">
            {/* BACKGROUND IMAGE WITH BLUR */}
            <motion.div
                initial={{ scale: 1.1, opacity: 0 }}
                animate={{ scale: 1, opacity: 0.6 }}
                transition={{ duration: 2 }}
                className="absolute inset-0 bg-cover bg-center"
                style={{ backgroundImage: `url('/images/loading_bg_${bgIndex}.png')` }}
            />

            {/* VINETA OVERLAY */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.8)_100%)]" />

            {/* CONTENT CONTAINER */}
            <div className="relative z-10 w-full max-w-xl px-8 flex flex-col items-center">

                {/* LOGO AREA */}
                <motion.div
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="mb-12 flex flex-col items-center"
                >
                    <div className="relative">
                        <BrainCircuit className="w-16 h-16 text-teal-500 mb-4" />
                        <motion.div
                            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                            transition={{ repeat: Infinity, duration: 2 }}
                            className="absolute inset-0 bg-teal-500/20 blur-xl rounded-full"
                        />
                    </div>
                    <h1 className="text-3xl font-black tracking-[0.3em] uppercase text-white drop-shadow-[0_0_10px_rgba(20,184,166,0.5)]">
                        Oracle Link
                    </h1>
                    <div className="h-0.5 w-24 bg-gradient-to-r from-transparent via-teal-500 to-transparent mt-2" />
                </motion.div>

                {/* PROGRESS BAR SECTION */}
                <div className="w-full space-y-2 mb-12">
                    <div className="flex justify-between items-end mb-1">
                        <span className="text-[10px] uppercase font-bold tracking-widest text-teal-400 flex items-center gap-2">
                            <Sparkles className="w-3 h-3 animate-pulse" />
                            Procesando Destino
                        </span>
                        <span className="text-2xl font-black text-white italic">
                            {progress}%
                        </span>
                    </div>

                    <div className="h-2 w-full bg-white/5 border border-white/10 rounded-full overflow-hidden backdrop-blur-sm">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            className="h-full bg-gradient-to-r from-teal-600 via-teal-400 to-white shadow-[0_0_15px_rgba(20,184,166,0.8)]"
                        />
                    </div>
                </div>

                {/* QUOTES SECTION */}
                <div className="text-center space-y-4">
                    <AnimatePresence mode="wait">
                        <motion.p
                            key={quote1}
                            initial={{ y: 10, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            exit={{ y: -10, opacity: 0 }}
                            className="text-teal-100/80 text-sm font-medium italic"
                        >
                            "{quote1}"
                        </motion.p>
                    </AnimatePresence>

                    <AnimatePresence mode="wait">
                        <motion.p
                            key={quote2}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 0.6 }}
                            className="text-zinc-400 text-[11px] uppercase tracking-widest font-bold"
                        >
                            {quote2}
                        </motion.p>
                    </AnimatePresence>
                </div>

                {/* FOOTER INFO */}
                <div className="absolute bottom-12 flex items-center gap-6 opacity-30 text-[9px] font-bold uppercase tracking-[0.2em] text-white">
                    <span className="flex items-center gap-1"><Zap className="w-3 h-3" /> Neural Analysis</span>
                    <span className="flex items-center gap-1"><ShieldAlert className="w-3 h-3" /> Oracle Secure</span>
                </div>

            </div>


            <div className="loading-scanlines" />
        </div>
    );
}
