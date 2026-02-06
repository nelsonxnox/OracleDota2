"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sparkles, User, Mail, Lock, ArrowRight, Gamepad2 } from "lucide-react";
import { motion } from "framer-motion";
import { auth } from "@/lib/firebase";
import { signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from "firebase/auth";

import { Suspense } from "react";

function LoginContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [method, setMethod] = useState<"email" | "dota_id">("email");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [dotaId, setDotaId] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    useEffect(() => {
        if (searchParams.get("registered") === "true") {
            setSuccess("¡Cuenta creada con éxito! Ahora puedes iniciar sesión.");
        }
    }, [searchParams]);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            await signInWithEmailAndPassword(auth, email, password);
            router.push("/dashboard");
        } catch (err: any) {
            console.error("Error en login:", err);
            setError("Credenciales inválidas. Por favor verifica tu correo y contraseña.");
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleLogin = async () => {
        const provider = new GoogleAuthProvider();
        try {
            await signInWithPopup(auth, provider);
            router.push("/dashboard");
        } catch (err: any) {
            console.error("Error en Google login:", err);
            setError("Error al iniciar sesión con Google.");
        }
    };

    return (
        <main className="min-h-screen bg-black text-zinc-100 flex items-center justify-center relative overflow-hidden font-sans">
            {/* Background Ambience */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-br from-black via-zinc-950 to-black z-0" />
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_center,_var(--tw-gradient-from)_0%,_transparent_70%)] from-zinc-800/20 to-transparent opacity-30 mix-blend-overlay" />
                <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-red-600/10 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-purple-600/10 blur-[150px] rounded-full animate-pulse delay-1000" />
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="relative z-10 w-full max-w-4xl grid md:grid-cols-2 gap-0 bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden shadow-2xl"
            >

                {/* Left Side: Visuals */}
                <div className="relative hidden md:flex flex-col items-center justify-center p-12 bg-zinc-900/80">
                    <div className="absolute inset-0 bg-gradient-to-br from-red-600/20 to-purple-600/20 mix-blend-overlay" />
                    <div className="relative z-10 text-center space-y-6">
                        <motion.div
                            initial={{ rotate: -10, opacity: 0 }}
                            animate={{ rotate: 0, opacity: 1 }}
                            transition={{ delay: 0.2, duration: 0.8 }}
                            className="h-16 w-16 mx-auto rounded-2xl bg-gradient-to-br from-white to-zinc-400 flex items-center justify-center shadow-[0_0_40px_rgba(255,255,255,0.2)]"
                        >
                            <Sparkles className="h-8 w-8 text-black" />
                        </motion.div>
                        <div>
                            <h2 className="text-3xl font-black uppercase italic tracking-tighter mb-2">Oracle<span className="text-red-600">Dota</span></h2>
                            <p className="text-zinc-400 text-sm font-medium tracking-wide">Tu camino al rango Inmortal comienza aquí.</p>
                        </div>
                    </div>
                </div>

                {/* Right Side: Form */}
                <div className="p-8 md:p-12 flex flex-col justify-center space-y-8 bg-black/40">
                    <div className="space-y-2">
                        <h1 className="text-2xl font-bold tracking-tight">Bienvenido de nuevo</h1>
                        <p className="text-zinc-500 text-sm">Ingresa tus credenciales para acceder al sistema.</p>
                    </div>

                    {success && (
                        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-500 text-xs font-bold text-center">
                            {success}
                        </div>
                    )}

                    {error && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-xs font-bold text-center">
                            {error}
                        </div>
                    )}

                    <div className="flex gap-2 p-1 bg-zinc-900/80 rounded-lg border border-white/5">
                        <button
                            onClick={() => setMethod("email")}
                            className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-bold uppercase tracking-wider rounded-md transition-all ${method === "email" ? "bg-zinc-800 text-white shadow-lg" : "text-zinc-500 hover:text-zinc-300"
                                }`}
                        >
                            <Mail className="h-3 w-3" /> Email
                        </button>
                        <button
                            onClick={() => setMethod("dota_id")}
                            className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-bold uppercase tracking-wider rounded-md transition-all ${method === "dota_id" ? "bg-zinc-800 text-white shadow-lg" : "text-zinc-500 hover:text-zinc-300"
                                }`}
                        >
                            <Gamepad2 className="h-3 w-3" /> Steam/Friend ID
                        </button>
                    </div>

                    <form className="space-y-4" onSubmit={handleLogin}>
                        <div className="space-y-4">
                            {method === "email" ? (
                                <div className="space-y-2" key="email-input">
                                    <label className="text-xs font-bold uppercase text-zinc-500 ml-1">Correo Electrónico</label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                        <Input
                                            type="email"
                                            placeholder="usuario@ejemplo.com"
                                            required
                                            className="pl-9 bg-zinc-950/50 border-zinc-800 focus:border-red-600/50 transition-colors"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                        />
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-2" key="dota-id-input">
                                    <label className="text-xs font-bold uppercase text-zinc-500 ml-1">Dota 2 Friend ID</label>
                                    <div className="relative">
                                        <User className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                        <Input
                                            type="text"
                                            placeholder="EJ: 123456789"
                                            className="pl-9 bg-zinc-950/50 border-zinc-800 focus:border-red-600/50 transition-colors"
                                            value={dotaId}
                                            onChange={(e) => setDotaId(e.target.value)}
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="space-y-2">
                                <div className="flex justify-between items-center">
                                    <label className="text-xs font-bold uppercase text-zinc-500 ml-1">Contraseña</label>
                                    <Link href="#" className="text-[10px] text-red-500 hover:text-red-400 font-bold uppercase tracking-wider">
                                        ¿Olvidaste tu clave?
                                    </Link>
                                </div>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                                    <Input
                                        type="password"
                                        placeholder="••••••••"
                                        required
                                        className="pl-9 bg-zinc-950/50 border-zinc-800 focus:border-red-600/50 transition-colors"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                    />
                                </div>
                            </div>
                        </div>

                        <Button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-red-600 to-red-800 hover:from-red-500 hover:to-red-700 text-white font-bold tracking-widest uppercase py-6 shadow-[0_0_20px_rgba(220,38,38,0.3)]"
                        >
                            {loading ? "Cargando..." : "Iniciar Sesión"} <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </form>

                    <div className="relative">
                        <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-zinc-800"></div></div>
                        <div className="relative flex justify-center text-xs uppercase"><span className="bg-zinc-950 px-2 text-zinc-600 font-bold">O continúa con</span></div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <Button
                            variant="outline"
                            onClick={handleGoogleLogin}
                            className="border-zinc-800 bg-zinc-900/50 hover:bg-zinc-800 hover:text-white text-zinc-400 font-bold uppercase text-[10px] tracking-wider"
                        >
                            <svg className="mr-2 h-3 w-3" viewBox="0 0 24 24"><path fill="currentColor" d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z" /></svg>
                            Google
                        </Button>
                        <Button variant="outline" className="border-zinc-800 bg-zinc-900/50 hover:bg-zinc-800 hover:text-white text-zinc-400 font-bold uppercase text-[10px] tracking-wider">
                            <div className="mr-2 h-3 w-3 bg-white rounded-full flex items-center justify-center text-black font-black text-[8px]">S</div>
                            Steam
                        </Button>
                    </div>

                    <p className="text-center text-xs text-zinc-500">
                        ¿No tienes cuenta?{" "}
                        <Link href="/register" className="text-white hover:text-red-500 font-bold transition-colors underline decoration-zinc-700 underline-offset-4">
                            Regístrate gratis
                        </Link>
                    </p>
                </div>
            </motion.div>

            {/* Footer Signature */}
            <div className="absolute bottom-4 left-0 right-0 text-center pointer-events-none opacity-30">
                <p className="text-[10px] uppercase tracking-[0.3em] text-zinc-500 font-black">
                    © {new Date().getFullYear()} Nelson Planes Arencibia
                </p>
            </div>
        </main>
    );
}

export default function LoginPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-black flex items-center justify-center text-zinc-500 font-bold uppercase tracking-widest text-xs animate-pulse">
                Cargando Portal...
            </div>
        }>
            <LoginContent />
        </Suspense>
    );
}
