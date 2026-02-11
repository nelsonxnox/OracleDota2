"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

interface PlanCardProps {
  name: string;
  price: string;
  matches: number;
  features: string[];
  highlighted?: boolean;
  onSelect: () => void;
}

function PlanCard({ name, price, matches, features, highlighted, onSelect }: PlanCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className={`relative p-8 rounded-2xl border-2 ${
        highlighted
          ? "border-purple-500 bg-gradient-to-br from-purple-900/30 to-blue-900/30"
          : "border-gray-700 bg-gray-800/50"
      } backdrop-blur-sm`}
    >
      {highlighted && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-purple-600 text-white px-4 py-1 rounded-full text-sm font-bold">
          MÁS POPULAR
        </div>
      )}
      
      <h3 className="text-2xl font-bold text-white mb-2">{name}</h3>
      <div className="mb-6">
        <span className="text-5xl font-bold text-white">{price}</span>
        <span className="text-gray-400 ml-2">USD</span>
      </div>
      
      <div className="mb-6">
        <p className="text-3xl font-bold text-purple-400">{matches} Partidas</p>
        <p className="text-gray-400 text-sm mt-1">
          ${(parseFloat(price.replace("$", "")) / matches).toFixed(2)} por partida
        </p>
      </div>
      
      <ul className="space-y-3 mb-8">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center text-gray-300">
            <svg
              className="w-5 h-5 text-green-500 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            {feature}
          </li>
        ))}
      </ul>
      
      <button
        onClick={onSelect}
        className={`w-full py-3 rounded-lg font-bold transition-all ${
          highlighted
            ? "bg-purple-600 hover:bg-purple-700 text-white"
            : "bg-gray-700 hover:bg-gray-600 text-white"
        }`}
      >
        Seleccionar Plan
      </button>
    </motion.div>
  );
}

export default function PlansPage() {
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const handleSelectPlan = (planType: string, matches: number, price: number) => {
    setSelectedPlan(planType);
    
    // TODO: Integrar con Stripe/PayPal
    alert(`Plan seleccionado: ${planType}\n${matches} partidas por $${price}\n\nIntegración de pago próximamente...`);
    
    // Aquí iría la lógica de pago
    // Por ahora, redirigir al dashboard
    // router.push("/dashboard");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold text-white mb-4">
            Planes de Oracle Coach
          </h1>
          <p className="text-xl text-gray-300">
            Elige el plan que mejor se adapte a tu estilo de juego
          </p>
        </motion.div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <PlanCard
              name="Plan Básico"
              price="$1.99"
              matches={10}
              features={[
                "10 partidas con Oracle",
                "Análisis en vivo durante el juego",
                "Alertas de timing (Runas, Lotos)",
                "Consejos tácticos cada 5 minutos",
                "Análisis de muertes",
              ]}
              onSelect={() => handleSelectPlan("basic", 10, 1.99)}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <PlanCard
              name="Plan Premium"
              price="$2.50"
              matches={50}
              features={[
                "50 partidas con Oracle",
                "Análisis en vivo durante el juego",
                "Alertas de timing (Runas, Lotos)",
                "Consejos tácticos cada 5 minutos",
                "Análisis de muertes",
                "Soporte prioritario",
              ]}
              highlighted={true}
              onSelect={() => handleSelectPlan("premium", 50, 2.50)}
            />
          </motion.div>
        </div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700"
        >
          <h2 className="text-3xl font-bold text-white mb-6 text-center">
            ¿Qué incluye Oracle Coach?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl mb-3">🎮</div>
              <h3 className="text-xl font-bold text-white mb-2">Análisis en Vivo</h3>
              <p className="text-gray-400">
                Oracle te guía durante la partida con consejos tácticos basados en el estado del juego
              </p>
            </div>
            
            <div className="text-center">
              <div className="text-4xl mb-3">⏰</div>
              <h3 className="text-xl font-bold text-white mb-2">Alertas de Timing</h3>
              <p className="text-gray-400">
                Nunca pierdas Runas de Sabiduría, Lotos o Tormentores con nuestras alertas precisas
              </p>
            </div>
            
            <div className="text-center">
              <div className="text-4xl mb-3">📊</div>
              <h3 className="text-xl font-bold text-white mb-2">Análisis Táctico</h3>
              <p className="text-gray-400">
                Cada 5 minutos recibes un informe detallado de tu rendimiento y el de tu equipo
              </p>
            </div>
          </div>
        </motion.div>

        {/* Back Button */}
        <div className="text-center mt-8">
          <button
            onClick={() => router.push("/dashboard")}
            className="text-purple-400 hover:text-purple-300 transition-colors"
          >
            ← Volver al Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
