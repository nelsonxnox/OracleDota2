"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bitcoin, Coffee, Heart, Zap, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function DonatePage() {
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

                <div className="grid md:grid-cols-2 gap-6">
                    {/* Crypto Donations */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <Card className="bg-zinc-900/40 border-teal-500/20 h-full backdrop-blur-md">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-3 text-teal-400">
                                    <Bitcoin className="w-6 h-6" />
                                    Criptomonedas
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <p className="text-zinc-400 text-sm leading-relaxed">
                                    La forma más directa de apoyar sin intermediarios. Ideal para usuarios en Cuba.
                                </p>

                                <div className="space-y-4">
                                    <div className="bg-black/40 p-3 rounded-lg border border-zinc-800 group hover:border-teal-500/30 transition-colors">
                                        <p className="text-[10px] text-zinc-500 font-bold uppercase mb-1">USDT (TRC20)</p>
                                        <code className="text-teal-400 text-xs break-all block font-mono">
                                            TC8U3YgS9hR8zL4PzW9H2nS6mK5jV1qR4t (Placeholder)
                                        </code>
                                    </div>
                                    <div className="bg-black/40 p-3 rounded-lg border border-zinc-800 group hover:border-orange-500/30 transition-colors">
                                        <p className="text-[10px] text-zinc-500 font-bold uppercase mb-1">Bitcoin (BTC)</p>
                                        <code className="text-orange-400 text-xs break-all block font-mono">
                                            bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh (Placeholder)
                                        </code>
                                    </div>
                                </div>

                                <div className="p-4 bg-teal-500/5 rounded-xl border border-teal-500/10">
                                    <p className="text-xs text-teal-300">
                                        💡 Una vez donado, envía un correo a <span className="font-bold underline">soporte@oracledota.com</span> con tu ID de usuario para activar el rango Donor.
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>

                    {/* Digital Payments */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <Card className="bg-zinc-900/40 border-rose-500/20 h-full backdrop-blur-md">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-3 text-rose-400">
                                    <Coffee className="w-6 h-6" />
                                    Digital Support
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <p className="text-zinc-400 text-sm leading-relaxed">
                                    Para donaciones con PayPal, Tarjeta o Apple/Google Pay.
                                </p>

                                <div className="space-y-3">
                                    <Button
                                        className="w-full bg-rose-600 hover:bg-rose-500 text-white font-bold h-12 gap-2"
                                        onClick={() => window.open("https://ko-fi.com/oracledota", "_blank")}
                                    >
                                        <Heart size={18} fill="currentColor" /> Donar en Ko-fi
                                    </Button>
                                    <Button
                                        variant="outline"
                                        className="w-full border-zinc-700 bg-transparent hover:bg-zinc-800 text-zinc-300 h-12 gap-2"
                                        onClick={() => window.open("https://www.buymeacoffee.com/oracledota", "_blank")}
                                    >
                                        <Zap size={18} /> Buy me a Coffee
                                    </Button>
                                </div>

                                <div className="flex items-center gap-4 pt-4 grayscale opacity-50">
                                    <div className="h-4 w-auto bg-zinc-800 rounded px-2 text-[10px] flex items-center">STRIPE</div>
                                    <div className="h-4 w-auto bg-zinc-800 rounded px-2 text-[10px] flex items-center">PAYPAL</div>
                                    <div className="h-4 w-auto bg-zinc-800 rounded px-2 text-[10px] flex items-center">VISA</div>
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
                    <h3 className="text-xl font-bold mb-4">Beneficios del Rango <span className="text-teal-400">Donor</span></h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="space-y-2">
                            <div className="text-teal-400 font-black text-2xl">20</div>
                            <p className="text-xs text-zinc-500 font-bold uppercase">Preguntas Diarias</p>
                        </div>
                        <div className="space-y-2">
                            <div className="text-teal-400 font-black text-2xl">FULL</div>
                            <p className="text-xs text-zinc-500 font-bold uppercase">Acceso RAG 2.0</p>
                        </div>
                        <div className="space-y-2">
                            <div className="text-teal-400 font-black text-2xl">VIP</div>
                            <p className="text-xs text-zinc-500 font-bold uppercase">Soporte Prioritario</p>
                        </div>
                    </div>
                </motion.div>

                <p className="text-center text-zinc-600 text-xs">
                    Oracle no está afiliado a Valve Corporation. Todos los logos son propiedad de sus respectivos dueños.
                </p>
            </div>
        </div>
    );
}
