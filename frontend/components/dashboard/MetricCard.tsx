"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { clsx } from "clsx";

interface MetricCardProps {
  label: string;
  value: string;
  change: string;
  positive: boolean;
  icon: React.ReactNode;
  color: "cyan" | "fraud" | "warning" | "safe" | "purple";
  subtitle?: string;
}

const COLOR_MAP = {
  cyan: {
    bg: "rgba(0, 245, 255, 0.08)",
    border: "rgba(0, 245, 255, 0.2)",
    iconBg: "rgba(0, 245, 255, 0.12)",
    iconColor: "#00F5FF",
    valueColor: "#00F5FF",
    glow: "0 0 20px rgba(0, 245, 255, 0.15)",
  },
  fraud: {
    bg: "rgba(255, 45, 85, 0.06)",
    border: "rgba(255, 45, 85, 0.2)",
    iconBg: "rgba(255, 45, 85, 0.12)",
    iconColor: "#FF2D55",
    valueColor: "#FF2D55",
    glow: "0 0 20px rgba(255, 45, 85, 0.1)",
  },
  warning: {
    bg: "rgba(255, 184, 0, 0.06)",
    border: "rgba(255, 184, 0, 0.2)",
    iconBg: "rgba(255, 184, 0, 0.12)",
    iconColor: "#FFB800",
    valueColor: "#FFB800",
    glow: "0 0 20px rgba(255, 184, 0, 0.1)",
  },
  safe: {
    bg: "rgba(0, 214, 143, 0.06)",
    border: "rgba(0, 214, 143, 0.2)",
    iconBg: "rgba(0, 214, 143, 0.12)",
    iconColor: "#00D68F",
    valueColor: "#00D68F",
    glow: "0 0 20px rgba(0, 214, 143, 0.1)",
  },
  purple: {
    bg: "rgba(124, 58, 237, 0.06)",
    border: "rgba(124, 58, 237, 0.2)",
    iconBg: "rgba(124, 58, 237, 0.12)",
    iconColor: "#a855f7",
    valueColor: "#a855f7",
    glow: "0 0 20px rgba(124, 58, 237, 0.1)",
  },
};

export default function MetricCard({
  label,
  value,
  change,
  positive,
  icon,
  color,
  subtitle,
}: MetricCardProps) {
  const colors = COLOR_MAP[color];
  const isNeutral = change === "0%" || change === "—";

  return (
    <motion.div
      whileHover={{ y: -2, scale: 1.01 }}
      transition={{ type: "spring", stiffness: 400, damping: 30 }}
      className="glass-card p-4 cursor-default"
      style={{
        background: colors.bg,
        borderColor: colors.border,
        boxShadow: `${colors.glow}, 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)`,
      }}
    >
      <div className="flex items-start justify-between mb-3">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: colors.iconBg, color: colors.iconColor }}
        >
          {icon}
        </div>
        <div
          className={clsx(
            "flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-lg",
            isNeutral
              ? "bg-white/5 text-white/40"
              : positive
              ? "bg-safe/10 text-safe"
              : "bg-fraud/10 text-fraud"
          )}
        >
          {isNeutral ? (
            <Minus className="w-3 h-3" />
          ) : positive ? (
            <TrendingUp className="w-3 h-3" />
          ) : (
            <TrendingDown className="w-3 h-3" />
          )}
          {change}
        </div>
      </div>

      <div>
        <p className="text-xs text-white/50 font-medium mb-1">{label}</p>
        <motion.p
          key={value}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-2xl font-bold"
          style={{ color: colors.valueColor }}
        >
          {value}
        </motion.p>
        {subtitle && (
          <p className="text-xs text-white/30 font-mono mt-0.5">{subtitle}</p>
        )}
      </div>
    </motion.div>
  );
}
