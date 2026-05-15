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
    default: "camoufox-turnstile · SDK Python",
    template: "%s · camoufox-turnstile",
  },
  description:
    "Integra Cloudflare Turnstile en automatizaciones con Camoufox y Playwright async. Modo visión YOLO o solo DOM.",
  keywords: [
    "Turnstile",
    "Cloudflare",
    "Camoufox",
    "Playwright",
    "Python",
    "SDK",
    "automation",
  ],
  authors: [{ name: "Builker", url: "https://builker.com" }],
  openGraph: {
    title: "camoufox-turnstile — SDK Python",
    description:
      "Turnstile con Camoufox y Playwright: modo YOLO con inferencia y heurística DOM.",
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
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full scroll-smooth antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
