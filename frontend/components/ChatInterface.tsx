import { useState, useRef, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Send, Sparkles, Loader2, Zap, Ghost, Eye, X, Mic, MicOff, Volume2, VolumeX, ThumbsUp, ThumbsDown } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import axios from "axios";
import { API_BASE } from "@/lib/api";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
    role: "user" | "assistant";
    content: string;
    feedback?: "good" | "bad";
}

interface ChatInterfaceProps {
    matchId: string;
    isOpen: boolean;
    onToggle: () => void;
    hideButton?: boolean;
}

export default function ChatInterface({ matchId, isOpen, onToggle, hideButton = false }: ChatInterfaceProps) {
    const { user } = useAuth();
    const [messages, setMessages] = useState<Message[]>([
        { role: "assistant", content: "Bienvenido. Soy ORACLE, tu coach de Dota 2 en versión beta. Puedo ayudarte a analizar tus partidas y mejorar tu juego. Ten en cuenta que aún estoy en desarrollo y puedo cometer errores, así que si algo no te parece correcto, no dudes en pedirme que lo revise." }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);

    // Window State
    const [windowSize, setWindowSize] = useState({ width: 450, height: 600 });
    const constraintsRef = useRef(null);

    // Scroll Logic
    const scrollViewportRef = useRef<HTMLDivElement>(null);
    const [shouldAutoScroll, setShouldAutoScroll] = useState(true);

    const scrollToBottom = () => {
        if (scrollViewportRef.current) {
            scrollViewportRef.current.scrollTop = scrollViewportRef.current.scrollHeight;
        }
    };

    // Smart Scroll: Detect if user is at bottom
    const handleScroll = () => {
        if (!scrollViewportRef.current) return;
        const { scrollTop, scrollHeight, clientHeight } = scrollViewportRef.current;
        const isAtBottom = scrollHeight - scrollTop - clientHeight < 100; // 100px threshold
        setShouldAutoScroll(isAtBottom);
    };

    // Auto-scroll effect
    useEffect(() => {
        if (shouldAutoScroll) {
            scrollToBottom();
        }
    }, [messages, shouldAutoScroll]);

    // Initial load history
    useEffect(() => {
        if (isOpen) {
            const timeout = setTimeout(scrollToBottom, 100);
            const loadHistory = async () => {
                if (!user?.uid) return;
                try {
                    const res = await axios.get(`${API_BASE}/chat/history/${matchId}`, {
                        params: { user_id: user.uid }
                    });
                    if (res.data.history && res.data.history.length > 0) {
                        setMessages(res.data.history);
                    }
                } catch (e) {
                    console.error("Error loading history:", e);
                }
            };
            loadHistory();
            return () => clearTimeout(timeout);
        }
    }, [isOpen, user, matchId]); // Removed messages dependency to prevent excessive reloading

    // ... (Speech Recognition logic remains similar, simplified for brevity in this update structure)
    // Initialize Speech Recognition
    const recognitionRef = useRef<any>(null);
    useEffect(() => {
        if (typeof window !== "undefined" && ("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = false;
            recognitionRef.current.lang = "es-ES";
            recognitionRef.current.onresult = (event: any) => {
                setInput(event.results[0][0].transcript);
                setIsListening(false);
            };
            recognitionRef.current.onerror = () => setIsListening(false);
            recognitionRef.current.onend = () => setIsListening(false);
        }
    }, []);

    const toggleListening = () => {
        if (isListening) recognitionRef.current?.stop();
        else {
            setInput("");
            setIsListening(true);
            recognitionRef.current?.start();
        }
    };

    // Text to Speech
    const speak = useCallback(async (text: string, force: boolean = false) => {
        if (!force && !isVoiceEnabled) return;
        try {
            const cleanText = text.replace(/[*_#`~]/g, "").trim();
            if (!cleanText) return;
            const response = await axios.post(`${API_BASE}/tts`, { text: cleanText }, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            new Audio(url).play();
        } catch (error) {
            console.error("[TTS] Error:", error);
        }
    }, [isVoiceEnabled]);

    const handleSend = async (textOverride?: string) => {
        const textToSend = textOverride || input;
        if (!textToSend.trim()) return;

        setInput("");
        // Optimistically add user message
        setMessages((prev) => [...prev, { role: "user", content: textToSend }]);
        setShouldAutoScroll(true); // Force scroll on send
        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE}/chat`, {
                match_id: matchId,
                query: textToSend,
                user_id: user?.uid || "guest"
            });
            setMessages((prev) => [...prev, { role: "assistant", content: response.data.response }]);
        } catch (error: any) {
            let errorMessage = "Error de conexión con el Oráculo.";

            if (error.response?.data?.detail?.error === "daily_limit_reached") {
                const detail = error.response.data.detail;
                const resetHours = detail.reset_in_hours || 24;
                errorMessage = `🚫 ${detail.message}\n\n` +
                    `❓ Usadas hoy: ${detail.questions_used}/${detail.limit}\n` +
                    `⏰ Reset en: ${resetHours}h\n\n` +
                    `💚 Apoya el proyecto: visitando la sección de Donaciones.`;
            } else if (error.code === "ERR_NETWORK") {
                errorMessage = "⚠️ No se puede conectar al servidor. Verifica tu conexión a internet.";
            }

            setMessages((prev) => [...prev, {
                role: "assistant",
                content: errorMessage
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleFeedback = async (messageIndex: number, feedback: "good" | "bad") => {
        // Get the message and the preceding user question if available
        const msg = messages[messageIndex];
        const precedingUserMsg = messages.slice(0, messageIndex).reverse().find(m => m.role === "user");

        // Optimistic UI update
        setMessages(prev => prev.map((m, i) => i === messageIndex ? { ...m, feedback } : m));

        try {
            await axios.post(`${API_BASE}/chat/feedback`, {
                user_id: user?.uid || "guest",
                match_id: matchId,
                message_content: msg.content,
                feedback,
                question: precedingUserMsg?.content || ""
            });
        } catch (error) {
            console.error("[FEEDBACK] Error sending feedback:", error);
            // Revert on error
            setMessages(prev => prev.map((m, i) => i === messageIndex ? { ...m, feedback: undefined } : m));
        }
    };

    return (
        <>
            {/* FLOATING ACTION BUTTON */}
            {!isOpen && !hideButton && (
                <motion.div
                    className="fixed bottom-12 right-12 z-[100]"
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                >
                    <div className="relative group">
                        <div className="absolute inset-0 bg-teal-500 blur-xl opacity-40 animate-pulse" />
                        <Button
                            onClick={onToggle}
                            className="h-16 w-16 rounded-full bg-[#0a0a14] border-2 border-teal-500/50 shadow-2xl flex items-center justify-center relative z-10 hover:border-teal-400 transition-colors"
                        >
                            <Eye className="w-8 h-8 text-teal-400" />
                        </Button>
                    </div>
                </motion.div>
            )}

            {/* DRAGGABLE CHAT WINDOW */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        transition={{ type: "spring", stiffness: 200, damping: 25 }}
                        className="fixed z-[99] top-24 right-12" // Initial position
                        style={{ width: windowSize.width, height: windowSize.height }}
                    >
                        {/* DRAG HANDLE (Global click outside implies drag? No, use explicit header) */}
                        <motion.div
                            drag
                            dragMomentum={false}
                            className="w-full h-full flex flex-col bg-[#0a0a14]/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden relative"
                        >
                            {/* HEADER (Draggable Area) */}
                            <div className="h-14 shrink-0 bg-white/5 border-b border-white/5 flex items-center justify-between px-4 cursor-grab active:cursor-grabbing" onPointerDown={(e) => e.stopPropagation()}>
                                <div className="flex items-center gap-2 pointer-events-none">
                                    <div className="w-2 h-2 rounded-full bg-teal-500 animate-pulse" />
                                    <span className="text-xs font-black uppercase tracking-widest text-zinc-300">Oracle Link v2.0</span>
                                </div>
                                <div className="flex items-center gap-1" onPointerDown={(e) => e.stopPropagation()}>
                                    <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-400 hover:text-white" onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}>
                                        {isVoiceEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
                                    </Button>
                                    <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-400 hover:text-rose-500" onClick={onToggle}>
                                        <X size={18} />
                                    </Button>
                                </div>
                            </div>

                            {/* MESSAGES AREA */}
                            <div
                                className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent"
                                ref={scrollViewportRef}
                                onScroll={handleScroll}
                                onPointerDown={(e) => e.stopPropagation()} // Allow text selection
                            >
                                <div className="p-4 rounded-xl bg-teal-900/10 border border-teal-500/20 mb-6 mx-4">
                                    <p className="text-[11px] text-teal-300 text-center font-bold uppercase tracking-widest opacity-70">
                                        "Los hilos del destino son visibles..."
                                    </p>
                                </div>

                                {messages.map((msg, i) => (
                                    <div key={i} className={cn("flex flex-col gap-1", msg.role === "user" ? "items-end" : "items-start")}>
                                        <div className={cn(
                                            "max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed relative group",
                                            msg.role === "user"
                                                ? "bg-zinc-800 text-zinc-100 rounded-tr-none"
                                                : "bg-teal-950/40 text-teal-50 border border-teal-500/10 rounded-tl-none"
                                        )}>
                                            {msg.role === "assistant" && (
                                                <button
                                                    onClick={() => speak(msg.content, true)}
                                                    className="absolute -right-8 top-1 p-1.5 text-zinc-500 hover:text-teal-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                                >
                                                    <Volume2 size={14} />
                                                </button>
                                            )}
                                            {msg.content}
                                        </div>
                                        {msg.role === "assistant" && (
                                            <div className="flex items-center gap-1 px-1">
                                                <button
                                                    disabled={!!msg.feedback}
                                                    onClick={() => handleFeedback(i, "good")}
                                                    title="Respuesta útil"
                                                    className={cn(
                                                        "p-1.5 rounded-lg transition-all",
                                                        msg.feedback === "good"
                                                            ? "text-emerald-400 bg-emerald-400/10"
                                                            : "text-zinc-600 hover:text-emerald-400 hover:bg-emerald-400/10",
                                                        msg.feedback && msg.feedback !== "good" && "opacity-30 cursor-not-allowed"
                                                    )}
                                                >
                                                    <ThumbsUp size={12} />
                                                </button>
                                                <button
                                                    disabled={!!msg.feedback}
                                                    onClick={() => handleFeedback(i, "bad")}
                                                    title="Respuesta incorrecta"
                                                    className={cn(
                                                        "p-1.5 rounded-lg transition-all",
                                                        msg.feedback === "bad"
                                                            ? "text-rose-400 bg-rose-400/10"
                                                            : "text-zinc-600 hover:text-rose-400 hover:bg-rose-400/10",
                                                        msg.feedback && msg.feedback !== "bad" && "opacity-30 cursor-not-allowed"
                                                    )}
                                                >
                                                    <ThumbsDown size={12} />
                                                </button>
                                                {msg.feedback && (
                                                    <span className="text-[9px] text-zinc-600 ml-1">
                                                        {msg.feedback === "good" ? "¡Gracias!" : "Gracias por el aviso"}
                                                    </span>
                                                )}
                                            </div>
                                        )}
                                        <span className="text-[9px] font-bold uppercase text-zinc-600 px-1">{msg.role === "user" ? "Tú" : "Oráculo"}</span>
                                    </div>
                                ))}
                                {loading && (
                                    <div className="flex gap-1 px-4 py-2">
                                        <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-bounce" />
                                        <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-bounce delay-75" />
                                        <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-bounce delay-150" />
                                    </div>
                                )}
                            </div>

                            {/* INPUT AREA */}
                            <div className="p-4 bg-black/20 border-t border-white/5 shrink-0" onPointerDown={(e) => e.stopPropagation()}>
                                <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
                                    <Button
                                        type="button"
                                        onClick={toggleListening}
                                        className={cn("h-10 w-10 shrink-0 rounded-xl", isListening ? "bg-red-500/20 text-red-500" : "bg-zinc-800 text-zinc-400")}
                                    >
                                        {isListening ? <Mic size={18} className="animate-pulse" /> : <MicOff size={18} />}
                                    </Button>
                                    <Input
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        placeholder="Consulta al Oráculo..."
                                        className="bg-black/40 border-white/10 text-sm h-10 rounded-xl focus-visible:ring-teal-500/50"
                                    />
                                    <Button type="submit" disabled={!input.trim() || loading} className="h-10 w-10 shrink-0 bg-teal-600 hover:bg-teal-500 text-white rounded-xl">
                                        <Send size={18} />
                                    </Button>
                                </form>
                            </div>

                            {/* RESIZE HANDLE */}
                            <div
                                className="absolute bottom-0 right-0 w-6 h-6 cursor-nwse-resize z-50 flex items-center justify-center group"
                                onPointerDown={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    const startX = e.clientX;
                                    const startY = e.clientY;
                                    const startWidth = windowSize.width;
                                    const startHeight = windowSize.height;

                                    const onMove = (moveEvent: PointerEvent) => {
                                        setWindowSize({
                                            width: Math.max(300, startWidth + (moveEvent.clientX - startX)),
                                            height: Math.max(400, startHeight + (moveEvent.clientY - startY))
                                        });
                                    };
                                    const onUp = () => {
                                        document.removeEventListener("pointermove", onMove);
                                        document.removeEventListener("pointerup", onUp);
                                    };
                                    document.addEventListener("pointermove", onMove);
                                    document.addEventListener("pointerup", onUp);
                                }}
                            >
                                <div className="w-3 h-3 border-r-2 border-b-2 border-zinc-600 group-hover:border-teal-400 transition-colors rounded-br-sm" />
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
