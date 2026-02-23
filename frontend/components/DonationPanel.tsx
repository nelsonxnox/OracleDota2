"use client";

import { Check, Heart, Bitcoin, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function DonationPanel() {
    const router = useRouter();

    const tiers = [
        {
            name: "Estándar",
            price: "$0",
            period: "Para siempre",
            icon: Check,
            color: "from-gray-600 to-gray-800",
            features: [
                "3 consultas diarias de IA",
                "Análisis de perfiles básico",
                "Estadísticas públicas"
            ],
            buttonText: "Plan Actual",
            disabled: true
        },
        {
            name: "Donador",
            price: "Cualquier",
            period: "donación",
            icon: Heart,
            color: "from-teal-600 to-cyan-600",
            popular: true,
            features: [
                "Hasta 20 consultas diarias",
                "Prioridad en servidores de IA",
                "Acceso completo a RAG 2.0",
                "Badge VIP en perfil",
                "Soporte prioritario"
            ],
            buttonText: "Apoyar Proyecto",
            action: () => router.push("/donate")
        }
    ];

    return (
        <div className="space-y-8 py-8">
            <div className="text-center space-y-4">
                <h2 className="text-3xl md:text-5xl font-black uppercase italic tracking-tighter">
                    Apoya a <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-500 to-cyan-500">Oracle</span>
                </h2>
                <p className="text-zinc-400 max-w-2xl mx-auto text-lg">
                    Oracle es 100% gratuito. Las donaciones nos ayudan a mantener los servidores y mejorar la IA.
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto px-4">
                {tiers.map((tier, idx) => {
                    const Icon = tier.icon;
                    return (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            viewport={{ once: true }}
                            className={`relative bg-zinc-900/40 backdrop-blur-xl border ${tier.popular ? "border-teal-500/50 shadow-[0_0_30px_rgba(20,184,166,0.15)]" : "border-white/10"
                                } rounded-[2rem] p-8 space-y-8 hover:bg-zinc-900/60 transition-all duration-300 group flex flex-col`}
                        >
                            {tier.popular && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-6 py-1.5 bg-gradient-to-r from-teal-600 to-cyan-600 rounded-full text-xs font-black uppercase tracking-widest shadow-lg">
                                    Apoya el Proyecto
                                </div>
                            )}

                            <div className="text-center space-y-4">
                                <div className={`h-20 w-20 mx-auto rounded-3xl bg-gradient-to-br ${tier.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                                    <Icon className="h-10 w-10 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-2xl font-black uppercase tracking-wide">{tier.name}</h3>
                                    <div className="mt-2 flex items-baseline justify-center gap-1">
                                        <span className="text-4xl font-black text-white">{tier.price}</span>
                                        <span className="text-sm text-zinc-500 font-bold uppercase">{tier.period}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex-grow">
                                <ul className="space-y-4">
                                    {tier.features.map((feature, i) => (
                                        <li key={i} className="flex items-start gap-3">
                                            <div className={`mt-1 h-5 w-5 rounded-full bg-gradient-to-br ${tier.color} flex items-center justify-center flex-shrink-0`}>
                                                <Check className="h-3 w-3 text-white" />
                                            </div>
                                            <span className="text-sm text-zinc-300 font-medium leading-tight">{feature}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <Button
                                onClick={tier.action}
                                disabled={tier.disabled}
                                className={`w-full py-7 font-black uppercase tracking-widest text-sm rounded-xl transition-all duration-300 ${tier.popular
                                    ? "bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 text-white shadow-lg hover:shadow-cyan-500/25"
                                    : "bg-zinc-800 hover:bg-zinc-700 text-zinc-400 cursor-not-allowed"
                                    }`}
                            >
                                {tier.buttonText}
                            </Button>
                        </motion.div>
                    );
                })}
            </div>

            {/* Donation Methods Preview */}
            <div className="max-w-4xl mx-auto px-4">
                <div className="bg-zinc-900/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                    <h3 className="text-xl font-bold text-center mb-4 text-zinc-300">Métodos de Donación</h3>
                    <div className="flex justify-center gap-12 flex-wrap">
                        <div className="text-center group transition-all hover:scale-110">
                            <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center border border-blue-500/20 mb-2 mx-auto">
                                <Zap className="w-6 h-6 text-blue-500" />
                            </div>
                            <p className="text-[10px] text-zinc-500 font-black uppercase tracking-widest">QvaPay</p>
                        </div>
                        <div className="text-center group transition-all hover:scale-110">
                            <div className="w-12 h-12 bg-teal-500/10 rounded-xl flex items-center justify-center border border-teal-500/20 mb-2 mx-auto">
                                <Bitcoin className="w-6 h-6 text-teal-500" />
                            </div>
                            <p className="text-[10px] text-zinc-500 font-black uppercase tracking-widest">Crypto Directo</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
