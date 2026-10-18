/** @type {import('next').NextConfig} */
const nextConfig = {
  images: { unoptimized: true },
<<<<<<< HEAD
  async headers() {
    return [{ source: '/:path*', headers: [
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'X-Frame-Options', value: 'DENY' },
      { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
      { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
    ] }]
  },
=======
>>>>>>> b9d02d34e42932237d9f91969848006efc59b2b1
}
export default nextConfig
