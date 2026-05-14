import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";

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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap"
          rel="stylesheet"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#050813" />
      </head>
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
