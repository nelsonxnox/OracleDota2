"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Send, Sparkles, Loader2, Zap, Ghost, Eye, X, MessageSquareQuote } from "lucide-react";
import axios from "axios";
import { API_BASE } from "@/lib/api";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
    role: "user" | "assistant";
    content: string;
}

interface ChatInterfaceProps {
    matchId: string;
    isOpen: boolean;
    onToggle: () => void;
}

export default function ChatInterface({ matchId, isOpen, onToggle }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([
        { role: "assistant", content: "Los hilos del destino han sido revelados. Soy el Oráculo. ¿Deseas saber por qué el trono de tus aliados se convirtió en cenizas, o qué guerrero fue bendecido por la fortuna?" }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        if (isOpen) {
            const timeout = setTimeout(scrollToBottom, 100);
            return () => clearTimeout(timeout);
        }
    }, [messages, loading, isOpen]);

    const handleSend = async () => {
        if (!input.trim()) return;
        const userMsg = input;
        setInput("");
        setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE}/chat`, {
                match_id: matchId,
                query: userMsg
            });
            setMessages((prev) => [...prev, { role: "assistant", content: response.data.response }]);
        } catch (error) {
            setMessages((prev) => [...prev, { role: "assistant", content: "El velo del backend ha caído. Mis visiones están nubladas temporalmente." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {/* FLOATING ACTION BUTTON (FAB) - NOW CENTERED AND EPIC */}
            <motion.div
                className="fixed bottom-12 left-1/2 -translate-x-1/2 z-[100]"
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ type: "spring", damping: 15, stiffness: 150 }}
            >
                <div className="relative group">
                    {/* Concentric Glow Rings */}
                    <div className="absolute inset-0 rounded-full bg-teal-500/20 blur-2xl group-hover:bg-teal-500/40 transition-all duration-500 animate-pulse" />
                    <div className="absolute -inset-4 rounded-full border border-teal-500/10 animate-[ping_3s_linear_infinite] pointer-events-none" />
                    <div className="absolute -inset-8 rounded-full border border-teal-500/5 animate-[ping_4s_linear_infinite] pointer-events-none" />

                    <Button
                        onClick={onToggle}
                        className={cn(
                            "h-28 w-28 rounded-full shadow-[0_0_60px_rgba(20,184,166,0.6)] transition-all duration-700 flex flex-col items-center justify-center p-0 overflow-hidden border-4 relative",
                            isOpen
                                ? "bg-red-600 border-red-400 shadow-[0_0_80px_rgba(220,38,38,0.6)] scale-90"
                                : "bg-teal-600 border-teal-400 hover:scale-110 active:scale-95 shadow-[0_0_100px_rgba(20,184,166,0.8)]"
                        )}
                    >
                        {/* Scanline Effect Overlay */}
                        <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.5)_50%)] bg-[length:100%_4px] opacity-20 pointer-events-none" />

                        <AnimatePresence mode="wait">
                            {isOpen ? (
                                <motion.div
                                    key="close"
                                    initial={{ opacity: 0, rotate: 180 }}
                                    animate={{ opacity: 1, rotate: 0 }}
                                    exit={{ opacity: 0, rotate: -180 }}
                                >
                                    <X className="h-10 w-10 text-white" />
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="open"
                                    initial={{ opacity: 0, scale: 0.5 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 1.5 }}
                                    className="flex flex-col items-center"
                                >
                                    <div className="relative">
                                        <Eye className="h-14 w-14 text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.8)]" />
                                        <div className="absolute inset-0 bg-white/20 blur-md rounded-full animate-pulse" />
                                    </div>
                                    <span className="text-[10px] font-black uppercase tracking-[0.2em] mt-2 text-white/90 drop-shadow-md">
                                        Oracle Chat
                                    </span>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </Button>
                </div>
            </motion.div>


            {/* EPIC FLOATING CHAT PANEL */}
            <AnimatePresence>
                {isOpen && (
                    <>
                        {/* Backdrop Blur overlay */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={onToggle}
                            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[80] cursor-pointer"
                        />

                        <motion.div
                            initial={{ x: 650, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            exit={{ x: 650, opacity: 0 }}
                            transition={{ type: "spring", damping: 25, stiffness: 120 }}
                            className="fixed top-0 bottom-0 right-0 w-full max-w-[500px] z-[90] flex flex-col"
                        >
                            <Card className="flex flex-col h-full overflow-hidden border-l border-white/10 bg-[#0a0a14] shadow-2xl relative rounded-none backdrop-blur-md">

                                {/* Header: Compacto y Moderno */}
                                <CardHeader className="py-4 px-6 border-b border-white/5 bg-zinc-950/50 flex flex-row items-center justify-between shrink-0">
                                    <div className="flex items-center gap-3">
                                        <div className="h-2 w-2 rounded-full bg-teal-500 animate-pulse shadow-[0_0_8px_rgba(20,184,166,0.6)]" />
                                        <span className="text-[11px] font-black uppercase tracking-widest text-zinc-400">Oralce Neural Link</span>
                                    </div>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={onToggle}
                                        className="h-8 w-8 rounded-full hover:bg-white/5 text-zinc-500 hover:text-rose-500 transition-all"
                                    >
                                        <X size={18} />
                                    </Button>
                                </CardHeader>

                                {/* Chat area: Optimizado para lectura */}
                                <CardContent className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent">
                                    {/* Saludo inicial estilo banner */}
                                    <div className="p-4 mb-6 rounded-xl bg-teal-500/5 border border-teal-500/10 border-dashed text-center">
                                        <p className="text-[12px] font-bold text-teal-200/70 italic uppercase leading-relaxed">
                                            "SOPLO DE DESTINO, MORTAL. SOY TU ASISTENTE INMORTAL. PREGUNTA LO QUE DESEES REVELAR."
                                        </p>
                                    </div>

                                    {messages.map((msg, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className={cn("flex flex-col", msg.role === "user" ? "items-end" : "items-start")}
                                        >
                                            <div className={cn(
                                                "max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed",
                                                msg.role === "user"
                                                    ? "bg-zinc-800 text-zinc-100 rounded-tr-none shadow-lg"
                                                    : "bg-teal-900/40 text-teal-50 border border-teal-500/20 rounded-tl-none shadow-[0_0_20px_rgba(20,184,166,0.1)] shadow-inner"
                                            )}>
                                                <div className="whitespace-pre-wrap">
                                                    {msg.content}
                                                </div>
                                            </div>
                                            <span className="mt-1 text-[9px] font-medium text-zinc-600 px-1 uppercase tracking-tight">
                                                {msg.role === "user" ? "Yo" : "Oráculo"}
                                            </span>
                                        </motion.div>
                                    ))}

                                    {loading && (
                                        <div className="flex items-center gap-2 px-2 py-2">
                                            <Loader2 className="h-3 w-3 animate-spin text-teal-500" />
                                            <span className="text-[10px] uppercase font-bold text-teal-500/50 tracking-widest">Analizando...</span>
                                        </div>
                                    )}
                                    <div ref={messagesEndRef} />
                                </CardContent>

                                {/* Input area: Minimalista */}
                                <div className="p-4 border-t border-white/5 bg-zinc-950/80 backdrop-blur-md">
                                    <form
                                        onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                                        className="flex gap-2"
                                    >
                                        <Input
                                            value={input}
                                            onChange={(e) => setInput(e.target.value)}
                                            placeholder="Escribe tu consulta..."
                                            disabled={loading}
                                            className="h-11 bg-zinc-900/50 border-white/5 text-zinc-100 text-sm rounded-xl focus-visible:ring-1 focus-visible:ring-teal-500/50"
                                        />
                                        <Button
                                            type="submit"
                                            disabled={loading || !input.trim()}
                                            className="h-11 w-11 bg-teal-600 hover:bg-teal-500 text-white rounded-xl shadow-lg shrink-0 transition-transform active:scale-95"
                                        >
                                            <Send size={18} />
                                        </Button>
                                    </form>
                                </div>
                            </Card>
                        </motion.div>

                    </>
                )}
            </AnimatePresence>
        </>
    );
}
