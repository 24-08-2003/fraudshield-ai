import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep Space Palette
        space: {
          950: "#020408",
          900: "#050813",
          800: "#080e1f",
          700: "#0c1530",
          600: "#111c40",
          500: "#172350",
        },
        // Electric Cyan
        cyan: {
          400: "#22d3ee",
          500: "#06b6d4",
          DEFAULT: "#00F5FF",
          neon: "#00F5FF",
        },
        // Neon Purple
        purple: {
          neon: "#7C3AED",
          bright: "#a855f7",
          glow: "#c084fc",
        },
        // Fraud Red
        fraud: {
          DEFAULT: "#FF2D55",
          dark: "#cc2244",
          glow: "rgba(255, 45, 85, 0.3)",
        },
        // Safe Green
        safe: {
          DEFAULT: "#00D68F",
          dark: "#00a86b",
          glow: "rgba(0, 214, 143, 0.3)",
        },
        // Warning Amber
        warning: {
          DEFAULT: "#FFB800",
          dark: "#cc9300",
          glow: "rgba(255, 184, 0, 0.3)",
        },
        // Glass
        glass: {
          white: "rgba(255, 255, 255, 0.05)",
          border: "rgba(255, 255, 255, 0.08)",
          hover: "rgba(255, 255, 255, 0.1)",
        },
      },
      fontFamily: {
        sans: ["Space Grotesk", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "cyber-grid":
          "linear-gradient(rgba(0,245,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,245,255,0.03) 1px, transparent 1px)",
        "glow-cyan": "radial-gradient(ellipse at center, rgba(0,245,255,0.15) 0%, transparent 70%)",
        "glow-purple": "radial-gradient(ellipse at center, rgba(124,58,237,0.15) 0%, transparent 70%)",
      },
      backgroundSize: {
        "grid-40": "40px 40px",
      },
      boxShadow: {
        "glow-cyan": "0 0 20px rgba(0, 245, 255, 0.3), 0 0 40px rgba(0, 245, 255, 0.1)",
        "glow-purple": "0 0 20px rgba(124, 58, 237, 0.3), 0 0 40px rgba(124, 58, 237, 0.1)",
        "glow-fraud": "0 0 20px rgba(255, 45, 85, 0.4), 0 0 40px rgba(255, 45, 85, 0.2)",
        "glow-safe": "0 0 20px rgba(0, 214, 143, 0.3), 0 0 40px rgba(0, 214, 143, 0.1)",
        "glass": "0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.08)",
        "card": "0 4px 24px rgba(0, 0, 0, 0.5), 0 1px 0 rgba(255,255,255,0.05) inset",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "scan": "scan 3s linear infinite",
        "glow-pulse": "glowPulse 2s ease-in-out infinite",
        "float": "float 6s ease-in-out infinite",
        "grid-move": "gridMove 20s linear infinite",
        "slide-in-right": "slideInRight 0.4s ease-out",
        "slide-in-up": "slideInUp 0.3s ease-out",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100vh)" },
        },
        glowPulse: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        gridMove: {
          "0%": { backgroundPosition: "0 0" },
          "100%": { backgroundPosition: "40px 40px" },
        },
        slideInRight: {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        slideInUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};

export default config;
