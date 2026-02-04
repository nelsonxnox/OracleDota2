"use client";

import { useState } from "react";
import { X, Mail, Lock, Gamepad2, Sparkles, ArrowRight, UserPlus, LogIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion, AnimatePresence } from "framer-motion";
import { auth, db } from "@/lib/firebase";
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";
import { useRouter } from "next/navigation";

interface AuthModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
    const [mode, setMode] = useState<"login" | "register">("login");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [dotaId, setDotaId] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const router = useRouter();

    const handleAuth = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            if (mode === "login") {
                await signInWithEmailAndPassword(auth, email, password);
            } else {
                const userCredential = await createUserWithEmailAndPassword(auth, email, password);
                await setDoc(doc(db, "users", userCredential.user.uid), {
                    email,
                    dota_id: dotaId,
                    createdAt: new Date().toISOString(),
                    uid: userCredential.user.uid
                });
            }
            onClose();
            router.push("/dashboard");
        } catch (err: any) {
            console.error("Auth Error:", err);
            setError(err.code === "auth/user-not-found" || err.code === "auth/wrong-password"
                ? "Credenciales incorrectas"
                : "Ocurrió un error. Verifica tus datos.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/80 backdrop-blur-md"
                    />

                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        className="relative w-full max-w-md bg-zinc-900/90 border border-white/10 rounded-3xl overflow-hidden shadow-2xl"
                    >
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-teal-500 via-purple-500 to-teal-500 opacity-50" />

                        <button onClick={onClose} className="absolute top-4 right-4 text-zinc-500 hover:text-white transition-colors p-2">
                            <X size={20} />
                        </button>

                        <div className="p-8 space-y-8">
                            <div className="text-center space-y-2">
                                <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-teal-500 to-teal-900 flex items-center justify-center mx-auto shadow-[0_0_20px_rgba(20,184,166,0.2)] mb-4">
                                    <Sparkles className="h-6 w-6 text-white" />
                                </div>
                                <h2 className="text-2xl font-black uppercase italic tracking-tighter text-white">
                                    {mode === "login" ? "Iniciar Sesión" : "Crear Cuenta"}
                                </h2>
                                <p className="text-zinc-500 text-xs font-medium uppercase tracking-widest">
                                    {mode === "login" ? "Regresa al campo de batalla" : "Únete a la legión del Oráculo"}
                                </p>
                            </div>

                            <form onSubmit={handleAuth} className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black uppercase text-zinc-500 ml-1">Email</label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                        <Input
                                            type="email"
                                            required
                                            className="pl-9 bg-black/40 border-zinc-800"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                        />
                                    </div>
                                </div>

                                {mode === "register" && (
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black uppercase text-zinc-500 ml-1">Dota Friend ID</label>
                                        <div className="relative">
                                            <Gamepad2 className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                            <Input
                                                type="text"
                                                className="pl-9 bg-black/40 border-zinc-800"
                                                value={dotaId}
                                                onChange={(e) => setDotaId(e.target.value)}
                                            />
                                        </div>
                                    </div>
                                )}

                                <div className="space-y-2">
                                    <label className="text-[10px] font-black uppercase text-zinc-500 ml-1">Contraseña</label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                        <Input
                                            type="password"
                                            required
                                            className="pl-9 bg-black/40 border-zinc-800"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                        />
                                    </div>
                                </div>

                                {error && <p className="text-red-500 text-[10px] font-bold text-center uppercase tracking-widest">{error}</p>}

                                <Button
                                    disabled={loading}
                                    className="w-full h-12 bg-white text-black hover:bg-zinc-200 font-black uppercase tracking-widest text-[10px] rounded-xl transition-all"
                                >
                                    {loading ? "Procesando..." : mode === "login" ? "Entrar" : "Registrarse"}
                                    <ArrowRight size={14} className="ml-2" />
                                </Button>
                            </form>

                            <div className="text-center pt-4 border-t border-white/5">
                                <button
                                    onClick={() => setMode(mode === "login" ? "register" : "login")}
                                    className="text-[10px] font-black uppercase tracking-widest text-teal-500 hover:text-teal-400 transition-colors"
                                >
                                    {mode === "login" ? "¿No tienes cuenta? Regístrate" : "¿Ya tienes cuenta? Inicia Sesión"}
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
