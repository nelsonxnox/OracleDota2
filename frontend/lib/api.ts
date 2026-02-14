// Detección automática de entorno
const isLocal = typeof window !== 'undefined' &&
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const envApiBase = process.env.NEXT_PUBLIC_API_BASE || "";

// Si estamos en local, preferimos localhost:8000.
// Si estamos en producción, SOLO usamos la URL configurada (nunca localhost).
export const API_BASE = isLocal
    ? "http://localhost:8000"
    : (envApiBase || "https://oracledota2.onrender.com");

if (!envApiBase && !isLocal && typeof window !== 'undefined') {
    console.warn("ADVERTENCIA: NEXT_PUBLIC_API_BASE no está configurada, usando fallback a Render.");
}
