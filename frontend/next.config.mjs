/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    // API_URL is a server-side env var — safe for Railway runtime injection
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
