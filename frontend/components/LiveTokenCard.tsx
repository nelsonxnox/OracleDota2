"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Copy, RefreshCw, Check, Key } from "lucide-react";
import axios from "axios";
import { API_BASE } from "@/lib/api";

export default function LiveTokenCard() {
    const { user } = useAuth();
    const [token, setToken] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    // Load existing token on mount
    useEffect(() => {
        if (!user?.uid) return;

        const fetchToken = async () => {
            try {
                const res = await axios.get(`${API_BASE}/api/user/get-live-token`, {
                    params: { user_id: user.uid }
                });
                setToken(res.data.token);
            } catch (error: any) {
                // No token found yet, that's okay
                if (error.response?.status !== 404) {
                    console.error("Error fetching token:", error);
                }
            }
        };

        fetchToken();
    }, [user]);

    const generateToken = async () => {
        if (!user?.uid) return;

        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE}/api/user/generate-live-token`, null, {
                params: { user_id: user.uid }
            });
            setToken(res.data.token);
        } catch (error) {
            console.error("Error generating token:", error);
            alert("Error al generar token. Verifica la consola.");
        } finally {
            setLoading(false);
        }
    };

    const copyToken = () => {
        if (token) {
            navigator.clipboard.writeText(token);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <Card className="relative overflow-hidden border-teal-500/20 bg-zinc-900/40 backdrop-blur-2xl">
            {/* Background Effect */}
            <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-teal-500/5 blur-3xl" />

            <CardHeader>
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-500/10">
                        <Key className="h-5 w-5 text-teal-400" />
                    </div>
                    <div>
                        <CardTitle className="text-lg font-black uppercase tracking-tight text-white">
                            Access Token
                        </CardTitle>
                        <p className="text-xs text-zinc-500 font-bold uppercase tracking-wider">
                            Para Oracle Neural Link
                        </p>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                {token ? (
                    <>
                        <div className="rounded-xl border border-white/10 bg-black/40 p-4">
                            <p className="text-[10px] font-black uppercase tracking-widest text-zinc-600 mb-2">
                                Tu Token Único
                            </p>
                            <p className="break-all font-mono text-sm text-teal-400">
                                {token}
                            </p>
                        </div>

                        <div className="flex gap-2">
                            <Button
                                onClick={copyToken}
                                className="flex-1 bg-teal-600 hover:bg-teal-500 text-white font-bold"
                            >
                                {copied ? (
                                    <>
                                        <Check className="mr-2 h-4 w-4" />
                                        Copiado
                                    </>
                                ) : (
                                    <>
                                        <Copy className="mr-2 h-4 w-4" />
                                        Copiar Token
                                    </>
                                )}
                            </Button>
                            <Button
                                onClick={generateToken}
                                disabled={loading}
                                variant="outline"
                                className="border-white/10"
                            >
                                <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                            </Button>
                        </div>

                        <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/20 p-3">
                            <p className="text-[10px] font-bold text-yellow-400">
                                ⚠️ Pega este token en la aplicación de escritorio Oracle Neural Link para conectar.
                            </p>
                        </div>
                    </>
                ) : (
                    <div className="space-y-3">
                        <p className="text-sm text-zinc-400">
                            Genera un token para conectar la aplicación de escritorio a tu cuenta.
                        </p>
                        <Button
                            onClick={generateToken}
                            disabled={loading}
                            className="w-full bg-teal-600 hover:bg-teal-500 text-white font-bold"
                        >
                            {loading ? (
                                <>
                                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                                    Generando...
                                </>
                            ) : (
                                <>
                                    <Key className="mr-2 h-4 w-4" />
                                    Generar Nuevo Token
                                </>
                            )}
                        </Button>
                        <p className="text-[10px] text-zinc-500 text-center italic">
                            * Al generar un nuevo token, el anterior quedará invalidado.
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
