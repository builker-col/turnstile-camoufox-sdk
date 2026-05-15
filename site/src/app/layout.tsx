import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Documentación · camoufox-turnstile",
    template: "%s · camoufox-turnstile",
  },
  description:
    "SDK Python para Cloudflare Turnstile con Camoufox, Playwright async e inferencia YOLO en el paquete base.",
  keywords: [
    "Turnstile",
    "Cloudflare",
    "Camoufox",
    "Playwright",
    "Python",
    "YOLO",
    "SDK",
  ],
  authors: [{ name: "Builker", url: "https://builker.com" }],
  openGraph: {
    title: "camoufox-turnstile — Documentación",
    description:
      "Integración Turnstile con YOLO, pesos automáticos y fallback DOM opcional.",
    type: "website",
    locale: "es_ES",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="es" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body className="min-h-screen scroll-smooth font-sans text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
