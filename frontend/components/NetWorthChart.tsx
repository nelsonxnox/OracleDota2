"use client";

import { Card, CardContent } from "@/components/ui/card";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { TrendingUp, Coins } from "lucide-react";

interface NetWorthChartProps {
    goldAdvantage: number[];
}

export default function NetWorthChart({ goldAdvantage }: NetWorthChartProps) {
    if (!goldAdvantage || goldAdvantage.length === 0) {
        return (
            <div className="h-64 flex flex-col items-center justify-center text-zinc-700 space-y-4 bg-zinc-950/20 rounded-3xl border border-white/5 italic">
                <Coins className="h-8 w-8 opacity-20" />
                <p className="text-[10px] font-black uppercase tracking-widest">Los hilos del oro están rotos para esta crónica.</p>
            </div>
        );
    }

    const data = goldAdvantage.map((val, i) => ({
        minute: i,
        value: val,
    }));

    return (
        <div className="h-[350px] w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                        <linearGradient id="colorAdv" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                            <stop offset="45%" stopColor="#10b981" stopOpacity={0} />
                            <stop offset="55%" stopColor="#f43f5e" stopOpacity={0} />
                            <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.2} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff" vertical={false} strokeOpacity={0.03} />
                    <XAxis
                        dataKey="minute"
                        stroke="#52525b"
                        fontSize={9}
                        tickLine={false}
                        axisLine={false}
                        tick={{ fill: '#3f3f46', fontWeight: 900 }}
                        tickFormatter={(min) => `${min}'`}
                    />
                    <YAxis
                        stroke="#52525b"
                        fontSize={9}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => `${(Math.abs(value) / 1000).toFixed(0)}k`}
                        tick={{ fill: '#3f3f46', fontWeight: 900 }}
                    />
                    <Tooltip
                        cursor={{ stroke: '#52525b', strokeWidth: 1 }}
                        contentStyle={{
                            backgroundColor: "rgba(9, 9, 11, 0.95)",
                            backdropFilter: "blur(12px)",
                            borderColor: "rgba(255, 255, 255, 0.05)",
                            borderRadius: '16px',
                            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)',
                            padding: '12px'
                        }}
                        itemStyle={{ fontSize: '10px', fontWeight: '900', textTransform: 'uppercase' }}
                        labelStyle={{ fontSize: '9px', color: '#52525b', fontWeight: '900', marginBottom: '8px', letterSpacing: '0.1em' }}
                        formatter={(value: any) => [
                            <span className={value > 0 ? 'text-emerald-500' : 'text-rose-500'}>
                                {Math.abs(value).toLocaleString()} {value > 0 ? 'Radiant Lead' : 'Dire Lead'}
                            </span>,
                            'VENTAJA'
                        ]}
                        labelFormatter={(label) => `CRÓNICA MINUTO ${label}`}
                    />
                    <ReferenceLine y={0} stroke="rgba(255,255,255,0.05)" strokeWidth={1} />
                    <Area
                        type="monotone"
                        dataKey="value"
                        stroke={data[data.length - 1].value > 0 ? "#10b981" : "#f43f5e"}
                        fill="url(#colorAdv)"
                        strokeWidth={2}
                        animationDuration={2000}
                        dot={false}
                        activeDot={{ r: 4, stroke: '#fff', strokeWidth: 2, fill: '#ff4444' }}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
