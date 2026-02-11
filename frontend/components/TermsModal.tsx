"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface TermsModalProps {
    isOpen: boolean;
    onAccept: () => void;
    onDecline: () => void;
}

export default function TermsModal({ isOpen, onAccept, onDecline }: TermsModalProps) {
    const [hasScrolled, setHasScrolled] = useState(false);

    const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
        const element = e.currentTarget;
        const isAtBottom = element.scrollHeight - element.scrollTop <= element.clientHeight + 50;
        if (isAtBottom && !hasScrolled) {
            setHasScrolled(true);
        }
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
                onClick={onDecline}
            >
                <motion.div
                    initial={{ scale: 0.9, y: 20 }}
                    animate={{ scale: 1, y: 0 }}
                    exit={{ scale: 0.9, y: 20 }}
                    className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden border border-purple-500/30"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6">
                        <h2 className="text-3xl font-bold text-white text-center">
                            Términos de Uso y Condiciones
                        </h2>
                        <p className="text-white/90 text-center mt-2">
                            Oracle Dota 2 - AI Coaching Platform
                        </p>
                    </div>

                    {/* Content */}
                    <div
                        className="p-6 overflow-y-auto max-h-[60vh] text-gray-200 space-y-4"
                        onScroll={handleScroll}
                    >
                        <section>
                            <h3 className="text-xl font-bold text-purple-400 mb-3">📋 Información del Servicio</h3>
                            <div className="bg-gray-800/50 p-4 rounded-lg space-y-2">
                                <p><strong className="text-purple-300">Desarrollador:</strong> Nelson Planes Arencibia</p>
                                <p><strong className="text-purple-300">Contacto:</strong> nelsonplanes@gmail.com</p>
                                <p><strong className="text-purple-300">Naturaleza:</strong> Plataforma de código abierto para la comunidad de Dota 2</p>
                            </div>
                        </section>

                        <section>
                            <h3 className="text-xl font-bold text-purple-400 mb-3">🎮 ¿Qué es Oracle Dota 2?</h3>
                            <p className="text-gray-300">
                                Oracle Dota 2 es una plataforma de coaching con inteligencia artificial que te ayuda a mejorar en Dota 2 mediante:
                            </p>
                            <ul className="list-disc list-inside space-y-2 mt-2 text-gray-300">
                                <li>Análisis en tiempo real durante tus partidas</li>
                                <li>Consejos tácticos personalizados cada 5 minutos</li>
                                <li>Análisis post-partida con estadísticas detalladas</li>
                                <li>Alertas de timings importantes (Runas, Lotos, Tormentor)</li>
                            </ul>
                        </section>

                        <section>
                            <h3 className="text-xl font-bold text-purple-400 mb-3">🔧 Tecnologías Utilizadas</h3>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="bg-gray-800/50 p-3 rounded">
                                    <p className="font-semibold text-purple-300">Backend</p>
                                    <p className="text-sm text-gray-400">FastAPI, Python, Firebase</p>
                                </div>
                                <div className="bg-gray-800/50 p-3 rounded">
                                    <p className="font-semibold text-purple-300">IA</p>
                                    <p className="text-sm text-gray-400">OpenRouter, DeepSeek, Gemini</p>
                                </div>
                                <div className="bg-gray-800/50 p-3 rounded">
                                    <p className="font-semibold text-purple-300">Datos</p>
                                    <p className="text-sm text-gray-400">OpenDota, Stratz, Valve GSI</p>
                                </div>
                                <div className="bg-gray-800/50 p-3 rounded">
                                    <p className="font-semibold text-purple-300">Frontend</p>
                                    <p className="text-sm text-gray-400">Next.js, React, TailwindCSS</p>
                                </div>
                            </div>
                        </section>

                        <section>
                            <h3 className="text-xl font-bold text-purple-400 mb-3">💰 Sistema de Tokens</h3>
                            <div className="space-y-2">
                                <div className="bg-gray-800/50 p-3 rounded">
                                    <p className="font-semibold text-green-400">Cuenta Gratuita</p>
                                    <p className="text-sm text-gray-300">1 token (1 partida con coaching)</p>
                                </div>
                                <div className="bg-gray-800/50 p-3 rounded">
                                    <p className="font-semibold text-blue-400">Plan Básico</p>
                                    <p className="text-sm text-gray-300">$1.99 USD - 10 partidas ($0.20/partida)</p>
                                </div>
                                <div className="bg-gray-800/50 p-3 rounded">
                                    <p className="font-semibold text-purple-400">Plan Premium</p>
                                    <p className="text-sm text-gray-300">$2.50 USD - 50 partidas ($0.05/partida)</p>
                                </div>
                            </div>
                            <p className="text-yellow-400 text-sm mt-3">
                                ⚠️ Los tokens se consumen automáticamente al iniciar una partida y NO son reembolsables una vez usados.
                            </p>
                        </section>

                        <section>
                            <h3 className="text-xl font-bold text-purple-400 mb-3">🔒 Privacidad y Datos</h3>
                            <p className="text-gray-300 mb-2">Recopilamos y procesamos:</p>
                            <ul className="list-disc list-inside space-y-1 text-gray-300">
                                <li>Tu correo electrónico (para autenticación)</li>
                                <li>Historial de partidas analizadas</li>
                                <li>Consultas al AI Coach</li>
                                <li>Estadísticas de uso del servicio</li>
                            </ul>
                            <p className="text-green-400 text-sm mt-3">
                                ✅ NO vendemos tus datos a terceros. Almacenamos en Firebase (Google Cloud) con cumplimiento GDPR.
                            </p>
                        </section>

                        <section>
                            <h3 className="text-xl font-bold text-purple-400 mb-3">✅ Uso Permitido</h3>
                            <ul className="list-disc list-inside space-y-1 text-gray-300">
                                <li>Usar el servicio para análisis personal de partidas</li>
                                <li>Compartir insights obtenidos</li>
                                <li>Contribuir al proyecto de código abierto</li>
                                <li>Reportar bugs y sugerir mejoras</li>
                            </ul>
                        </section>

                        <section>
                            <h3 className="text-xl font-bold text-red-400 mb-3">❌ Uso Prohibido</h3>
                            <ul className="list-disc list-inside space-y-1 text-gray-300">
                                <li>Hacer trampa o violar los TOS de Steam/Dota 2</li>
                                <li>Abusar del sistema de tokens o intentar fraude</li>
                                <li>Realizar ataques DDoS o comprometer la seguridad</li>
                                <li>Usar bots o scripts automatizados maliciosamente</li>
                            </ul>
                            <p className="text-red-400 text-sm mt-3">
                                ⚠️ La violación puede resultar en suspensión permanente y pérdida de tokens sin reembolso.
                            </p>
                        </section>

                        <section>
                            <h3 className="text-xl font-bold text-purple-400 mb-3">⚖️ Limitaciones de Responsabilidad</h3>
                            <div className="bg-yellow-900/20 border border-yellow-500/30 p-4 rounded-lg">
                                <p className="text-yellow-300 font-semibold mb-2">El servicio se proporciona "TAL CUAL":</p>
                                <ul className="list-disc list-inside space-y-1 text-gray-300 text-sm">
                                    <li>Los consejos de la IA son sugerencias, no garantías de victoria</li>
                                    <li>La IA puede cometer errores o proporcionar información inexacta</li>
                                    <li>No garantizamos disponibilidad 24/7 ni ausencia de errores</li>
                                    <li>No somos responsables por suspensiones de cuentas de Steam</li>
                                    <li>Dependemos de servicios de terceros (OpenDota, Firebase, etc.)</li>
                                </ul>
                            </div>
                        </section>

                        <section>
                            <h3 className="text-xl font-bold text-purple-400 mb-3">🤝 Proyecto Comunitario</h3>
                            <div className="bg-blue-900/20 border border-blue-500/30 p-4 rounded-lg">
                                <p className="text-blue-300 font-semibold mb-2">¡Necesitamos tu ayuda!</p>
                                <p className="text-gray-300 text-sm mb-2">
                                    Oracle Dota 2 es un proyecto de código abierto mantenido por la comunidad. Si tienes habilidades en:
                                </p>
                                <div className="grid grid-cols-2 gap-2 text-sm text-gray-300">
                                    <div>• Desarrollo Backend (Python)</div>
                                    <div>• Desarrollo Frontend (React)</div>
                                    <div>• Machine Learning / AI</div>
                                    <div>• Diseño UI/UX</div>
                                    <div>• Testing y QA</div>
                                    <div>• Documentación</div>
                                </div>
                                <p className="text-blue-400 mt-3 font-semibold">
                                    📧 Contacta a: nelsonplanes@gmail.com
                                </p>
                            </div>
                        </section>

                        <section>
                            <h3 className="text-xl font-bold text-purple-400 mb-3">📄 Información Legal</h3>
                            <ul className="space-y-2 text-sm text-gray-300">
                                <li>• <strong>Licencia:</strong> MIT (código abierto)</li>
                                <li>• <strong>Afiliación:</strong> NO afiliado con Valve Corporation</li>
                                <li>• <strong>Compatibilidad:</strong> Usa solo APIs oficiales de Valve (GSI)</li>
                                <li>• <strong>Última actualización:</strong> 11 de febrero de 2026</li>
                            </ul>
                        </section>

                        <section className="bg-purple-900/20 border border-purple-500/30 p-4 rounded-lg">
                            <h3 className="text-xl font-bold text-purple-400 mb-3">📜 Términos Completos</h3>
                            <p className="text-gray-300 text-sm mb-2">
                                Este es un resumen. Los términos completos están disponibles en:
                            </p>
                            <a
                                href="/TERMS_OF_SERVICE.md"
                                target="_blank"
                                className="text-blue-400 hover:text-blue-300 underline text-sm"
                            >
                                Ver Términos Completos (Documento Completo)
                            </a>
                        </section>

                        {!hasScrolled && (
                            <div className="sticky bottom-0 bg-gradient-to-t from-gray-900 to-transparent pt-8 pb-2 text-center">
                                <p className="text-yellow-400 animate-bounce">
                                    ⬇️ Desplázate hasta el final para aceptar
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="bg-gray-900 p-6 border-t border-gray-700">
                        <div className="flex items-center justify-between gap-4">
                            <button
                                onClick={onDecline}
                                className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition-colors"
                            >
                                Rechazar
                            </button>
                            <button
                                onClick={onAccept}
                                disabled={!hasScrolled}
                                className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${hasScrolled
                                        ? "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
                                        : "bg-gray-600 text-gray-400 cursor-not-allowed"
                                    }`}
                            >
                                {hasScrolled ? "✅ Acepto los Términos" : "Lee hasta el final"}
                            </button>
                        </div>
                        <p className="text-gray-400 text-xs text-center mt-3">
                            Al aceptar, confirmas que has leído y comprendido los términos de uso
                        </p>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
