import Link from 'next/link'
import { AlertTriangle } from 'lucide-react'

export default function NotFound() {
    return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center text-red-500 gap-4">
            <AlertTriangle className="w-16 h-16 opacity-50" />
            <h1 className="text-xl font-bold uppercase tracking-widest">404 - Página No Encontrada</h1>
            <p className="text-zinc-500">La página que buscas no existe en este plano de realidad.</p>
            <Link href="/">
                <button className="px-6 py-2 bg-red-900/20 border border-red-900/50 rounded hover:bg-red-900/40 transition text-red-400 mt-4">
                    Retorno a Base
                </button>
            </Link>
        </div>
    )
}
