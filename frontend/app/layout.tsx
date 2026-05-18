import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-space-grotesk",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "FraudShield AI — MLOps Fraud Detection Platform",
  description:
    "Production-grade credit card fraud detection powered by XGBoost, MLflow, and real-time monitoring. Built for fintech teams that need reliability.",
  keywords: ["fraud detection", "MLOps", "fintech", "machine learning", "credit card"],
  authors: [{ name: "FraudShield AI" }],
  openGraph: {
    title: "FraudShield AI",
    description: "Production-grade fraud detection platform",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#050813",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`dark ${spaceGrotesk.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-space-900 text-white antialiased">
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "rgba(8, 14, 31, 0.95)",
              color: "rgba(255,255,255,0.9)",
              border: "1px solid rgba(0, 245, 255, 0.2)",
              backdropFilter: "blur(20px)",
              borderRadius: "12px",
              fontFamily: "Space Grotesk, sans-serif",
            },
          }}
        />
      </body>
    </html>
  );
}
