"use client";

import { Check, Zap, Crown, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function PlansPanel() {
    const router = useRouter();

    const plans = [
        {
            name: "Gratuito",
            price: "$0",
            period: "Para siempre",
            icon: Zap,
            color: "from-gray-600 to-gray-800",
            features: [
                "1 token de coaching en vivo al mes",
                "3 preguntas al mes al AI Coach",
                "Análisis básico de partidas",
                "Acceso a estadísticas públicas"
            ],
            buttonText: "Plan Actual"
        },
        {
            name: "Básico",
            price: "$1.99",
            period: "/mes",
            icon: Rocket,
            color: "from-blue-600 to-cyan-600",
            popular: true,
            features: [
                "10 tokens de coaching en vivo",
                "Preguntas ILIMITADAS al AI Coach",
                "Análisis avanzado de partidas",
                "Recomendaciones personalizadas",
                "Soporte prioritario"
            ],
            buttonText: "Mejorar Ahora"
        },
        {
            name: "Premium",
            price: "$2.50",
            period: "/mes",
            icon: Crown,
            color: "from-purple-600 to-pink-600",
            features: [
                "50 tokens de coaching en vivo",
                "Preguntas ILIMITADAS al AI Coach",
                "Análisis profundo con IA avanzada (Deep Mode)",
                "Recomendaciones en tiempo real",
                "Acceso anticipado a nuevas funciones",
                "Soporte VIP 24/7" // Highlighted value proposition
            ],
            buttonText: "Obtener Premium"
        }
    ];

    return (
        <div className="space-y-8 py-8">
            <div className="text-center space-y-4">
                <h2 className="text-3xl md:text-5xl font-black uppercase italic tracking-tighter">
                    Elige tu <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-blue-500">Destino</span>
                </h2>
                <p className="text-zinc-400 max-w-2xl mx-auto text-lg">
                    Desbloquea todo el potencial de Oracle y acelera tu ascenso a Inmortal.
                </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto px-4">
                {plans.map((plan, idx) => {
                    const Icon = plan.icon;
                    return (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            viewport={{ once: true }}
                            className={`relative bg-zinc-900/40 backdrop-blur-xl border ${plan.popular ? "border-blue-500/50 shadow-[0_0_30px_rgba(59,130,246,0.15)]" : "border-white/10"
                                } rounded-[2rem] p-8 space-y-8 hover:bg-zinc-900/60 transition-all duration-300 group flex flex-col`}
                        >
                            {plan.popular && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-6 py-1.5 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-full text-xs font-black uppercase tracking-widest shadow-lg">
                                    Más Popular
                                </div>
                            )}

                            <div className="text-center space-y-4">
                                <div className={`h-20 w-20 mx-auto rounded-3xl bg-gradient-to-br ${plan.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                                    <Icon className="h-10 w-10 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-2xl font-black uppercase tracking-wide">{plan.name}</h3>
                                    <div className="mt-2 flex items-baseline justify-center gap-1">
                                        <span className="text-5xl font-black text-white">{plan.price}</span>
                                        <span className="text-sm text-zinc-500 font-bold uppercase">{plan.period}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex-grow">
                                <ul className="space-y-4">
                                    {plan.features.map((feature, i) => (
                                        <li key={i} className="flex items-start gap-3">
                                            <div className={`mt-1 h-5 w-5 rounded-full bg-gradient-to-br ${plan.color} flex items-center justify-center flex-shrink-0`}>
                                                <Check className="h-3 w-3 text-white" />
                                            </div>
                                            <span className="text-sm text-zinc-300 font-medium leading-tight">{feature}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <Button
                                onClick={() => router.push("/plans")}
                                className={`w-full py-7 font-black uppercase tracking-widest text-sm rounded-xl transition-all duration-300 ${plan.popular
                                        ? "bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white shadow-lg hover:shadow-cyan-500/25"
                                        : plan.price === "$0" ? "bg-zinc-800 hover:bg-zinc-700 text-zinc-400" : "bg-zinc-100 hover:bg-white text-black hover:scale-[1.02]"
                                    }`}
                            >
                                {plan.buttonText}
                            </Button>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
