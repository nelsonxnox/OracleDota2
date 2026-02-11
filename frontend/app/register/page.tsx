"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sparkles, User, Mail, Lock, ArrowLeft, Gamepad2, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import { auth, db } from "@/lib/firebase";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";
import TermsModal from "@/components/TermsModal";

export default function RegisterPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [dotaId, setDotaId] = useState("");
    const [error, setError] = useState("");
    const [showTerms, setShowTerms] = useState(false);
    const [termsAccepted, setTermsAccepted] = useState(false);

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        // Check if terms are accepted
        if (!termsAccepted) {
            setShowTerms(true);
            return;
        }

        if (password !== confirmPassword) {
            setError("Las contraseñas no coinciden");
            return;
        }

        setLoading(true);
        try {
            // 1. Crear usuario en Firebase Auth
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            // 2. Guardar datos adicionales en Firestore
            await setDoc(doc(db, "users", user.uid), {
                email: email,
                dota_id: dotaId,
                createdAt: new Date().toISOString(),
                uid: user.uid,
                termsAccepted: true,
                termsAcceptedAt: new Date().toISOString()
            });

            // 3. Redirigir al dashboard o login
            router.push("/login?registered=true");
        } catch (err: any) {
            console.error("Error en registro:", err);
            if (err.code === "auth/email-already-in-use") {
                setError("El correo ya está en uso.");
            } else if (err.code === "auth/weak-password") {
                setError("La contraseña es muy débil (mínimo 6 caracteres).");
            } else {
                setError("Ocurrió un error al registrar. Inténtalo de nuevo.");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleAcceptTerms = () => {
        setTermsAccepted(true);
        setShowTerms(false);
    };

    const handleDeclineTerms = () => {
        setShowTerms(false);
        setError("Debes aceptar los términos de uso para registrarte.");
    };

    return (
        <main className="min-h-screen bg-black text-zinc-100 flex items-center justify-center relative overflow-hidden font-sans">
            {/* Background Ambience */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-tl from-black via-zinc-950 to-black z-0" />
                <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-teal-600/5 blur-[120px] rounded-full animate-pulse" />
                <div className="absolute top-20 left-20 w-[300px] h-[300px] bg-indigo-600/5 blur-[100px] rounded-full" />
            </div>

            <div className="relative z-10 w-full max-w-lg p-6">
                <div className="mb-6 flex items-center gap-2 text-zinc-500 hover:text-white transition-colors cursor-pointer w-fit">
                    <ArrowLeft className="h-4 w-4" />
                    <Link href="/" className="text-xs font-bold uppercase tracking-widest">Volver al inicio</Link>
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden shadow-2xl p-8 md:p-10"
                >
                    <div className="text-center mb-8 space-y-2">
                        <h1 className="text-3xl font-black italic uppercase tracking-tighter">
                            Únete a <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-emerald-500">Oracle</span>
                        </h1>
                        <p className="text-zinc-400 text-sm font-medium">Crea tu cuenta y eleva tu nivel de juego.</p>
                    </div>

                    {error && (
                        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-xs font-bold text-center">
                            {error}
                        </div>
                    )}

                    <form className="space-y-4" onSubmit={handleRegister}>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase text-zinc-500 ml-1">Gmail / Correo</label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                    <Input
                                        type="email"
                                        placeholder="nombre@gmail.com"
                                        required
                                        className="pl-9 bg-zinc-950/50 border-zinc-800 focus:border-emerald-500/50"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                    />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase text-zinc-500 ml-1">Dota 2 Friend ID</label>
                                <div className="relative">
                                    <Gamepad2 className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                    <Input
                                        type="text"
                                        placeholder="EJ: 12345678"
                                        className="pl-9 bg-zinc-950/50 border-zinc-800 focus:border-emerald-500/50"
                                        value={dotaId}
                                        onChange={(e) => setDotaId(e.target.value)}
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-bold uppercase text-zinc-500 ml-1">Contraseña</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                <Input
                                    type="password"
                                    placeholder="Crea una contraseña segura"
                                    required
                                    className="pl-9 bg-zinc-950/50 border-zinc-800 focus:border-emerald-500/50"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-bold uppercase text-zinc-500 ml-1">Confirmar Contraseña</label>
                            <div className="relative">
                                <CheckCircle2 className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                <Input
                                    type="password"
                                    placeholder="Repite tu contraseña"
                                    required
                                    className="pl-9 bg-zinc-950/50 border-zinc-800 focus:border-emerald-500/50"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        {/* Terms and Conditions Checkbox */}
                        <div className="flex items-start gap-3 pt-2">
                            <input
                                type="checkbox"
                                id="terms"
                                checked={termsAccepted}
                                onChange={(e) => setTermsAccepted(e.target.checked)}
                                className="mt-1 h-4 w-4 rounded border-zinc-700 bg-zinc-950/50 text-emerald-600 focus:ring-emerald-500 focus:ring-offset-0"
                            />
                            <label htmlFor="terms" className="text-xs text-zinc-400">
                                Acepto los{" "}
                                <button
                                    type="button"
                                    onClick={() => setShowTerms(true)}
                                    className="text-emerald-400 hover:text-emerald-300 underline font-semibold"
                                >
                                    Términos de Uso y Condiciones
                                </button>
                                {" "}de Oracle Dota 2
                            </label>
                        </div>

                        <div className="pt-4">
                            <Button
                                type="submit"
                                disabled={loading || !termsAccepted}
                                className="w-full bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white font-bold tracking-widest uppercase py-6 shadow-[0_0_20px_rgba(20,184,166,0.2)] disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? "Creando cuenta..." : termsAccepted ? "Registrarse" : "Acepta los términos primero"}
                            </Button>
                        </div>
                    </form>

                    <p className="mt-6 text-center text-xs text-zinc-500">
                        ¿Ya tienes una cuenta?{" "}
                        <Link href="/login" className="text-emerald-400 hover:text-emerald-300 font-bold transition-colors underline decoration-zinc-700 underline-offset-4">
                            Inicia sesión aquí
                        </Link>
                    </p>
                </motion.div>

                {/* Footer Signature */}
                <div className="mt-8 text-center opacity-30">
                    <p className="text-[10px] uppercase tracking-[0.3em] text-zinc-500 font-black">
                        © {new Date().getFullYear()} Nelson Planes Arencibia
                    </p>
                </div>
            </div>

            {/* Terms Modal */}
            <TermsModal
                isOpen={showTerms}
                onAccept={handleAcceptTerms}
                onDecline={handleDeclineTerms}
            />
        </main>
    );
}
