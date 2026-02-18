const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      react: path.resolve(__dirname, 'node_modules/react'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
      'styled-jsx': path.resolve(__dirname, 'node_modules/styled-jsx'),
    };
    return config;
  },
};

module.exports = nextConfig;
