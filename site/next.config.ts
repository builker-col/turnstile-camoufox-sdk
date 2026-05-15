import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    // Evita que Next infiera la raíz del workspace en un lockfile fuera de `site/`.
    root: path.join(__dirname),
  },
};

export default nextConfig;
