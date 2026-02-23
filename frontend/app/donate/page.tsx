"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bitcoin, Coffee, Heart, Zap, ArrowLeft, Copy, User, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { useState } from "react";

export default function DonatePage() {
    const { user } = useAuth();
    const [copied, setCopied] = useState(false);

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    // Configuración de Donaciones
    const donationConfig = {
        usdt_trc20: "TDVwGhTde1WrvjFhkCRadA7WP2gE764KDU",
        btc: "bc1qges5zgktyzprh6au7f9tsuqtp2yqd5wajv8nu0",
        qvapay_url: "https://www.qvapay.com/pay/donacion-oracle"
    };

    return (
        <div className="min-h-screen bg-[#020205] text-white p-8 font-sans selection:bg-teal-500/30">
            <div className="max-w-4xl mx-auto space-y-12">
                {/* Back Button */}
                <Link href="/">
                    <Button variant="ghost" className="text-zinc-500 hover:text-teal-400 gap-2 mb-4">
                        <ArrowLeft size={16} /> Volver al Inicio
                    </Button>
                </Link>

                {/* Header */}
                <div className="text-center space-y-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-block px-4 py-1.5 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-xs font-bold uppercase tracking-widest"
                    >
                        Apoya el Proyecto
                    </motion.div>
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-6xl font-black tracking-tight"
                    >
                        El Destino de <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-cyan-300">Oracle</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="text-zinc-400 text-lg max-w-2xl mx-auto"
                    >
                        Oracle es gratuito para todos, con 3 consultas diarias. Tu apoyo nos permite mantener los servidores de IA y ampliar el límite a <span className="text-white font-bold">20 preguntas diarias</span>.
                    </motion.p>
                </div>

                {/* User ID Section - IMPORTANT for Manual Activation */}
                {user && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-zinc-900/60 border border-zinc-800 p-6 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6"
                    >
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-teal-500/10 rounded-xl">
                                <User className="text-teal-400" size={24} />
                            </div>
                            <div>
                                <p className="text-sm text-zinc-500 font-bold uppercase tracking-widest">Tu Identificador de Usuario</p>
                                <p className="text-lg font-mono text-zinc-300">{user.uid}</p>
                            </div>
                        </div>
                        <Button
                            variant="outline"
                            className="border-zinc-700 hover:border-teal-500/50 hover:bg-teal-500/5 gap-2"
                            onClick={() => copyToClipboard(user.uid)}
                        >
                            {copied ? <CheckCircle2 size={16} className="text-teal-400" /> : <Copy size={16} />}
                            {copied ? "¡Copiado!" : "Copiar ID"}
                        </Button>
                    </motion.div>
                )}

                <div className="max-w-2xl mx-auto">
                    {/* Main Donation Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <Card className="bg-zinc-900/40 border-teal-500/20 backdrop-blur-md overflow-hidden">
                            <CardHeader className="border-b border-white/5 bg-white/5">
                                <CardTitle className="flex items-center gap-3 text-teal-400 font-black uppercase tracking-wider">
                                    <Bitcoin className="w-6 h-6" />
                                    Donaciones (Cuba & Crypto)
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-8 p-8">
                                <div className="space-y-6">
                                    <Button
                                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-black h-14 text-lg gap-3 shadow-[0_0_20px_rgba(37,99,235,0.2)] transition-all"
                                        onClick={() => window.open(donationConfig.qvapay_url, "_blank")}
                                    >
                                        Donar con QvaPay
                                    </Button>

                                    <div className="relative py-2">
                                        <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-zinc-800"></span></div>
                                        <div className="relative flex justify-center text-[10px] uppercase font-bold tracking-[0.2em]"><span className="bg-[#020205] px-4 text-zinc-500">O mediante Crypto Directo</span></div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="bg-black/40 p-4 rounded-xl border border-zinc-800 group hover:border-teal-500/30 transition-all cursor-pointer"
                                            onClick={() => copyToClipboard(donationConfig.usdt_trc20)}>
                                            <p className="text-[10px] text-zinc-500 font-black uppercase mb-2 flex justify-between">
                                                <span>USDT (TRC20)</span>
                                                <span className="text-teal-400 opacity-60">Copiar</span>
                                            </p>
                                            <code className="text-teal-400 text-xs break-all block font-mono">
                                                {donationConfig.usdt_trc20}
                                            </code>
                                        </div>
                                        <div className="bg-black/40 p-4 rounded-xl border border-zinc-800 group hover:border-orange-500/30 transition-all cursor-pointer"
                                            onClick={() => copyToClipboard(donationConfig.btc)}>
                                            <p className="text-[10px] text-zinc-500 font-black uppercase mb-2 flex justify-between">
                                                <span>Bitcoin (BTC)</span>
                                                <span className="text-orange-500 opacity-60">Copiar</span>
                                            </p>
                                            <code className="text-orange-400 text-xs break-all block font-mono">
                                                {donationConfig.btc}
                                            </code>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-4 bg-teal-500/5 rounded-2xl border border-teal-500/10 flex items-center gap-4">
                                    <div className="text-2xl">💡</div>
                                    <p className="text-xs text-teal-300/80 leading-relaxed font-medium">
                                        Una vez donado, envía un correo a <span className="font-bold text-teal-400 underline">soporte@oracledota.com</span> con tu ID para activar el rango <span className="font-bold text-teal-400">Donor</span>.
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                </div>

                {/* Benefits */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="bg-gradient-to-r from-teal-900/20 to-zinc-900/20 p-8 rounded-2xl border border-white/5 text-center"
                >
                    <h3 className="text-xl font-bold mb-6">Beneficios del Rango <span className="text-teal-400 uppercase tracking-widest font-black">Donor</span></h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="space-y-2">
                            <div className="text-teal-400 font-black text-4xl italic tracking-tighter">20</div>
                            <p className="text-[10px] text-zinc-500 font-black uppercase tracking-widest">Consultas Diarias</p>
                        </div>
                        <div className="space-y-2">
                            <div className="text-teal-400 font-black text-4xl italic tracking-tighter">FULL</div>
                            <p className="text-[10px] text-zinc-500 font-black uppercase tracking-widest">Acceso RAG 2.0</p>
                        </div>
                        <div className="space-y-2">
                            <div className="text-teal-400 font-black text-4xl italic tracking-tighter">VIP</div>
                            <p className="text-[10px] text-zinc-500 font-black uppercase tracking-widest">Soporte Prioritario</p>
                        </div>
                    </div>
                </motion.div>

                <p className="text-center text-zinc-600 text-[10px] font-bold uppercase tracking-[0.3em] pb-8">
                    Oracle • El Destino te espera
                </p>
            </div>
        </div>
    );
}
