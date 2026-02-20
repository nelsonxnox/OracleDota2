const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: 'export', // Desactivado para rutas dinámicas
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  webpack: (config) => {
    // Esto asegura que use el React de la carpeta frontend
    config.resolve.alias['react'] = path.resolve(__dirname, 'node_modules', 'react');
    config.resolve.alias['react-dom'] = path.resolve(__dirname, 'node_modules', 'react-dom');
    return config;
  },
  // La sección 'experimental' con 'lucide-react' HA SIDO ELIMINADA para evitar el conflicto.
};

module.exports = nextConfig;