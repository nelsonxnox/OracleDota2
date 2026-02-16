const path = require('path');

const nextConfig = {
  // output: 'export', // Disabled for dynamic routes
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  webpack: (config) => {
    config.resolve.alias['react'] = path.resolve(__dirname, '../node_modules', 'react');
    config.resolve.alias['react-dom'] = path.resolve(__dirname, '../node_modules', 'react-dom');
    return config;
  },
};

module.exports = nextConfig;
