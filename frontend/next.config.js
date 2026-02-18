const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: 'export', // Desactivado para permitir rutas dinámicas
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  // Se eliminó la sección 'experimental' que causaba el error con lucide-react.
};

module.exports = nextConfig;
