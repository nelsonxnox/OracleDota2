"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bitcoin, Coffee, Heart, Zap, Users, Check, Copy } from "lucide-react";
import { useState } from "react";

export default function DonatePage() {
    const [copiedAddress, setCopiedAddress] = useState<string | null>(null);

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        setCopiedAddress(label);
        setTimeout(() => setCopiedAddress(null), 2000);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0a0a14] via-[#0f1419] to-[#0a0a14] p-8">
            <div className="max-w-5xl mx-auto space-y-8">
                {/* Header */}
                <div className="text-center space-y-4">
                    <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-teal-400 via-cyan-300 to-blue-400">
                        Apoya a Oracle
                    </h1>
                    <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
                        Oracle es 100% gratuito para todos. Las donaciones nos ayudan a mantener los servidores,
                        mejorar la IA y agregar nuevas funcionalidades.
                    </p>
                </div>

                {/* Benefits Comparison */}
                <div className="grid md:grid-cols-2 gap-6">
                    {/* Free Tier */}
                    <Card className="bg-zinc-900/50 border-zinc-700">
                        <CardHeader>
                            <CardTitle className="text-zinc-300">Plan Gratuito</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <div className="flex items-center gap-2 text-zinc-400">
                                <Check className="w-4 h-4 text-teal-500" />
                                <span>3 preguntas diarias al AI Coach</span>
                            </div>
                            <div className="flex items-center gap-2 text-zinc-400">
                                <Check className="w-4 h-4 text-teal-500" />
                                <span>Análisis básico de partidas</span>
                            </div>
                            <div className="flex items-center gap-2 text-zinc-400">
                                <Check className="w-4 h-4 text-teal-500" />
                                <span>Acceso a estadísticas</span>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Donor Tier */}
                    <Card className="bg-gradient-to-br from-teal-900/30 to-cyan-900/30 border-teal-500/50 relative overflow-hidden">
                        <div className="absolute top-0 right-0 bg-teal-500 text-black text-xs font-bold px-3 py-1 rounded-bl-lg">
                            DONADOR
                        </div>
                        <CardHeader>
                            <CardTitle className="text-teal-300">Plan Donador ⭐</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <div className="flex items-center gap-2 text-teal-100">
                                <Check className="w-4 h-4 text-teal-400" />
                                <span className="font-semibold">20 preguntas diarias al AI Coach</span>
                            </div>
                            <div className="flex items-center gap-2 text-teal-100">
                                <Check className="w-4 h-4 text-teal-400" />
                                <span>Análisis avanzado de partidas</span>
                            </div>
                            <div className="flex items-center gap-2 text-teal-100">
                                <Check className="w-4 h-4 text-teal-400" />
                                <span>Acceso prioritario a nuevas features</span>
                            </div>
                            <div className="flex items-center gap-2 text-teal-100">
                                <Check className="w-4 h-4 text-teal-400" />
                                <span>Tu nombre en la página de donadores</span>
                            </div>
                            <p className="text-xs text-teal-400 mt-4 italic">
                                * Cualquier donación te otorga acceso de por vida
                            </p>
                        </CardContent>
                    </Card>
                </div>

                {/* Patreon (Principal) */}
                <Card className="bg-gradient-to-r from-orange-900/20 to-red-900/20 border-orange-500/30">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-orange-400">
                            <Users className="w-6 h-6" />
                            Patreon - Apoya Mensualmente (Recomendado)
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-zinc-300 text-sm">
                            Conviértete en Patreon y ayuda a que Oracle siga creciendo. Ingresos recurrentes nos permiten planificar mejoras a largo plazo.
                        </p>

                        <div className="grid md:grid-cols-2 gap-4">
                            <div className="bg-black/40 p-4 rounded-lg border border-orange-700/50">
                                <p className="text-orange-400 font-bold mb-2">Tier 1: $2/mes</p>
                                <ul className="text-sm text-zinc-300 space-y-1">
                                    <li>✓ 20 preguntas diarias</li>
                                    <li>✓ Acceso a beta features</li>
                                    <li>✓ Rol especial en Discord</li>
                                </ul>
                            </div>
                            <div className="bg-black/40 p-4 rounded-lg border border-orange-700/50">
                                <p className="text-orange-400 font-bold mb-2">Tier 2: $5/mes</p>
                                <ul className="text-sm text-zinc-300 space-y-1">
                                    <li>✓ Todo lo anterior</li>
                                    <li>✓ Tu nombre en los créditos</li>
                                    <li>✓ Voto en nuevas features</li>
                                </ul>
                            </div>
                        </div>

                        <Button
                            className="w-full bg-orange-600 hover:bg-orange-500 text-white font-bold"
                            onClick={() => window.open("https://patreon.com/TU_USUARIO_AQUI", "_blank")}
                        >
                            <Heart className="w-4 h-4 mr-2" />
                            Unirse a Patreon
                        </Button>
                    </CardContent>
                </Card>

                {/* Crypto Donations */}
                <Card className="bg-zinc-900/50 border-teal-500/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-teal-400">
                            <Bitcoin className="w-6 h-6" />
                            Donación Única en Criptomonedas
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-zinc-300 text-sm">
                            Donaciones directas sin comisiones. Acepta USDT, Bitcoin, Litecoin, y más.
                        </p>

                        {/* Crypto Addresses */}
                        <div className="grid gap-3">
                            <div className="bg-black/40 p-4 rounded-lg border border-zinc-700 group">
                                <div className="flex items-center justify-between mb-2">
                                    <p className="text-xs text-zinc-500">USDT (TRC20) - Recomendado</p>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        className="h-6 text-xs"
                                        onClick={() => copyToClipboard("TU_DIRECCION_USDT_AQUI", "USDT")}
                                    >
                                        {copiedAddress === "USDT" ? (
                                            <Check className="w-3 h-3 text-green-500" />
                                        ) : (
                                            <Copy className="w-3 h-3" />
                                        )}
                                    </Button>
                                </div>
                                <code className="text-teal-400 text-sm break-all">TU_DIRECCION_USDT_AQUI</code>
                            </div>
                            <div className="bg-black/40 p-4 rounded-lg border border-zinc-700 group">
                                <div className="flex items-center justify-between mb-2">
                                    <p className="text-xs text-zinc-500">Bitcoin (BTC)</p>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        className="h-6 text-xs"
                                        onClick={() => copyToClipboard("TU_DIRECCION_BTC_AQUI", "BTC")}
                                    >
                                        {copiedAddress === "BTC" ? (
                                            <Check className="w-3 h-3 text-green-500" />
                                        ) : (
                                            <Copy className="w-3 h-3" />
                                        )}
                                    </Button>
                                </div>
                                <code className="text-orange-400 text-sm break-all">TU_DIRECCION_BTC_AQUI</code>
                            </div>
                            <div className="bg-black/40 p-4 rounded-lg border border-zinc-700 group">
                                <div className="flex items-center justify-between mb-2">
                                    <p className="text-xs text-zinc-500">Litecoin (LTC)</p>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        className="h-6 text-xs"
                                        onClick={() => copyToClipboard("TU_DIRECCION_LTC_AQUI", "LTC")}
                                    >
                                        {copiedAddress === "LTC" ? (
                                            <Check className="w-3 h-3 text-green-500" />
                                        ) : (
                                            <Copy className="w-3 h-3" />
                                        )}
                                    </Button>
                                </div>
                                <code className="text-blue-400 text-sm break-all">TU_DIRECCION_LTC_AQUI</code>
                            </div>
                        </div>

                        <p className="text-xs text-zinc-500 italic">
                            💡 Después de donar, envíanos un mensaje con tu ID de usuario y el hash de la transacción para activar tu tier de donador.
                        </p>
                    </CardContent>
                </Card>

                {/* Ko-fi */}
                <Card className="bg-zinc-900/50 border-blue-500/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-blue-400">
                            <Coffee className="w-6 h-6" />
                            Ko-fi - Donación con Tarjeta
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-zinc-300 text-sm">
                            Para donaciones con tarjeta de crédito/débito (PayPal, Stripe).
                        </p>
                        <Button
                            className="w-full bg-blue-600 hover:bg-blue-500"
                            onClick={() => window.open("https://ko-fi.com/TU_USUARIO", "_blank")}
                        >
                            <Heart className="w-4 h-4 mr-2" />
                            Donar en Ko-fi
                        </Button>
                    </CardContent>
                </Card>

                {/* Thank You Message */}
                <div className="text-center p-8 bg-gradient-to-r from-teal-900/20 to-cyan-900/20 rounded-xl border border-teal-500/20">
                    <p className="text-teal-300 font-bold text-xl mb-2">
                        ¡Gracias por apoyar a Oracle! 💚
                    </p>
                    <p className="text-zinc-400 text-sm">
                        Cada donación nos ayuda a mantener el proyecto vivo, pagar los servidores de IA,
                        y seguir mejorando la experiencia para toda la comunidad de Dota 2.
                    </p>
                </div>
            </div>
        </div>
    );
}
