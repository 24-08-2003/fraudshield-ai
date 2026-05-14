"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Menu, Bell, RefreshCw, Zap, Clock } from "lucide-react";

interface TopBarProps {
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export default function TopBar({ sidebarOpen, onToggleSidebar }: TopBarProps) {
  const [time, setTime] = useState<Date | null>(null);
  const [tps, setTps] = useState(28.4);
  const [alertCount, setAlertCount] = useState(3);

  useEffect(() => {
    setTime(new Date());
    const timer = setInterval(() => {
      setTime(new Date());
      setTps(+(Math.random() * 20 + 18).toFixed(1));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header
      className="h-14 flex items-center justify-between px-5 border-b border-white/8 flex-shrink-0"
      style={{ background: "rgba(5, 8, 19, 0.8)", backdropFilter: "blur(20px)" }}
    >
      {/* Left */}
      <div className="flex items-center gap-4">
        {!sidebarOpen && (
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-colors"
          >
            <Menu className="w-4 h-4" />
          </button>
        )}

        {/* Live TPS */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/3 border border-white/8">
          <Zap className="w-3.5 h-3.5 text-cyan-neon" />
          <span className="text-xs font-mono text-white/60">TPS</span>
          <motion.span
            key={tps}
            initial={{ opacity: 0.6, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-xs font-mono font-bold text-cyan-neon"
          >
            {tps}
          </motion.span>
        </div>

        {/* Model status */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-safe/10 border border-safe/20">
          <div className="w-1.5 h-1.5 rounded-full bg-safe animate-pulse" />
          <span className="text-xs font-mono text-safe">XGBoost Production v3</span>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-3">
        {/* Clock */}
        <div className="hidden sm:flex items-center gap-1.5 text-white/40">
          <Clock className="w-3.5 h-3.5" />
          <span className="text-xs font-mono">
            {time ? time.toLocaleTimeString("en-US", { hour12: false }) : "--:--:--"}
          </span>
          <span className="text-xs font-mono text-white/25">UTC</span>
        </div>

        {/* Refresh */}
        <button className="p-2 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-colors">
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* Alerts */}
        <button className="relative p-2 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-colors">
          <Bell className="w-4 h-4" />
          {alertCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-fraud rounded-full text-xs flex items-center justify-center text-white font-bold"
              style={{ fontSize: "9px" }}>
              {alertCount}
            </span>
          )}
        </button>

        {/* Avatar */}
        <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-space-900"
          style={{ background: "linear-gradient(135deg, #00F5FF, #7C3AED)" }}>
          FS
        </div>
      </div>
    </header>
  );
}
