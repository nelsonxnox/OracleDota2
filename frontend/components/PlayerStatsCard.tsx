"use client";

import { useEffect, useState } from "react";
import { Trophy, Target, Gamepad2, TrendingUp, AlertCircle, History, Zap } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { motion } from "framer-motion";

interface PlayerStats {
    winrate: number;
    total_games: number;
    versatility: number;
    rank_tier?: number;
}

export default function PlayerStatsCard({ accountId }: { accountId: string }) {
    const [stats, setStats] = useState<PlayerStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchStats = async () => {
            if (!accountId) return;

            try {
                setLoading(true);
                const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
                const res = await fetch(`${backendUrl}/api/player/${accountId}/stats`);

                if (!res.ok) {
                    throw new Error("Failed to fetch player stats");
                }

                const data = await res.json();
                setStats(data);
            } catch (err: any) {
                console.error("Error fetching player stats:", err);
                setError("Could not load stats");
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, [accountId]);

    if (loading) {
        return (
            <div className="grid grid-cols-3 gap-4 animate-pulse pt-4">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="h-24 bg-zinc-800/50 rounded-2xl border border-white/5" />
                ))}
            </div>
        );
    }

    if (error || !stats) {
        return (
            <div className="flex items-center gap-2 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs mt-4">
                <AlertCircle className="h-4 w-4" />
                <span>No se pudieron cargar las estadísticas. Verifica que tu perfil sea público.</span>
            </div>
        )
    }

    const statItems = [
        {
            label: "Win Rate",
            value: `${stats.winrate}%`,
            icon: Trophy,
            color: "text-yellow-500",
            bg: "bg-yellow-500/10 border-yellow-500/20"
        },
        {
            label: "Partidas",
            value: stats.total_games.toLocaleString(),
            icon: Gamepad2,
            color: "text-blue-500",
            bg: "bg-blue-500/10 border-blue-500/20"
        },
        {
            label: "Versatilidad",
            value: stats.versatility,
            icon: Target,
            color: "text-purple-500",
            bg: "bg-purple-500/10 border-purple-500/20"
        }
    ];

    return (
        <div className="grid grid-cols-3 gap-3 md:gap-4 pt-4">
            {statItems.map((item, idx) => {
                const Icon = item.icon;
                return (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.1 }}
                        className={`flex flex-col items-center justify-center p-3 md:p-4 rounded-2xl border ${item.bg} backdrop-blur-sm hover:scale-105 transition-transform`}
                    >
                        <Icon className={`h-5 w-5 md:h-6 md:w-6 ${item.color} mb-2`} />
                        <div className="text-xl md:text-2xl font-black text-white tracking-tight">{item.value}</div>
                        <div className="text-[10px] md:text-xs text-zinc-400 uppercase font-black tracking-wider text-center">{item.label}</div>
                    </motion.div>
                )
            })}
        </div>
    );
}
