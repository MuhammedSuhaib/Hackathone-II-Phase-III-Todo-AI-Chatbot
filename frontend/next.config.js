/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'mahmedmumair-phase3.hf.space',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
      },
    ],
  },
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://mahmedmumair-phase3.hf.space',
    NEXT_PUBLIC_DAPR_HTTP_PORT: process.env.NEXT_PUBLIC_DAPR_HTTP_PORT || '3500',
    NEXT_PUBLIC_DAPR_GRPC_PORT: process.env.NEXT_PUBLIC_DAPR_GRPC_PORT || '50001',
    NEXT_PUBLIC_BETTER_AUTH_URL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'https://mahmedmumair-phase3.hf.space',
  },
};

module.exports = nextConfig;