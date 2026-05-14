"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  BarChart3,
  BrainCircuit,
  GitBranch,
  Activity,
  Database,
  Shield,
  ChevronLeft,
  Settings,
  Bell,
  ExternalLink,
} from "lucide-react";
import { clsx } from "clsx";

const NAV_ITEMS = [
  {
    href: "/",
    label: "Overview",
    icon: LayoutDashboard,
    description: "Real-time dashboard",
  },
  {
    href: "/analytics",
    label: "Analytics",
    icon: BarChart3,
    description: "Fraud insights & trends",
  },
  {
    href: "/models",
    label: "Model Registry",
    icon: BrainCircuit,
    description: "MLflow model management",
  },
  {
    href: "/pipeline",
    label: "ML Pipeline",
    icon: GitBranch,
    description: "Airflow DAG status",
  },
  {
    href: "/monitoring",
    label: "Monitoring",
    icon: Activity,
    description: "Drift & Grafana metrics",
  },
  {
    href: "/data",
    label: "Data Ingestion",
    icon: Database,
    description: "CSV upload & API feeds",
  },
];

const EXTERNAL_LINKS = [
  { href: "http://localhost:5000", label: "MLflow UI", icon: ExternalLink },
  { href: "http://localhost:8080", label: "Airflow", icon: ExternalLink },
  { href: "http://localhost:3001", label: "Grafana", icon: ExternalLink },
];

interface SidebarProps {
  onClose: () => void;
}

export default function Sidebar({ onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen flex flex-col border-r border-white/8"
      style={{ background: "rgba(5, 8, 19, 0.95)", backdropFilter: "blur(20px)" }}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-5 py-5 border-b border-white/8">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, #00F5FF20, #7C3AED20)", border: "1px solid rgba(0,245,255,0.3)" }}>
              <Shield className="w-5 h-5 text-cyan-neon" />
            </div>
            <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-safe rounded-full"
              style={{ boxShadow: "0 0 6px #00D68F" }} />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white">FraudShield</h1>
            <p className="text-xs text-white/40 font-mono">AI v1.0.0</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-white/30 hover:text-white/70 hover:bg-white/5 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="text-xs font-semibold text-white/25 uppercase tracking-widest px-3 pb-2">
          Platform
        </p>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                whileHover={{ x: 2 }}
                className={clsx(
                  "nav-item group relative",
                  isActive && "active"
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="absolute inset-0 rounded-xl"
                    style={{
                      background: "rgba(0, 245, 255, 0.08)",
                      border: "1px solid rgba(0, 245, 255, 0.2)",
                    }}
                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
                  />
                )}
                <Icon className={clsx(
                  "w-4 h-4 relative z-10 transition-colors",
                  isActive ? "text-cyan-neon" : "text-white/40 group-hover:text-white/70"
                )} />
                <div className="relative z-10">
                  <span className={clsx(
                    "block text-sm font-medium",
                    isActive ? "text-cyan-neon" : "text-white/60 group-hover:text-white/90"
                  )}>
                    {item.label}
                  </span>
                </div>
                {isActive && (
                  <div className="ml-auto relative z-10 w-1.5 h-1.5 bg-cyan-neon rounded-full"
                    style={{ boxShadow: "0 0 6px #00F5FF" }} />
                )}
              </motion.div>
            </Link>
          );
        })}

        <div className="pt-4 pb-2">
          <p className="text-xs font-semibold text-white/25 uppercase tracking-widest px-3 pb-2">
            External Tools
          </p>
          {EXTERNAL_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              target="_blank"
              rel="noopener noreferrer"
              className="nav-item group"
            >
              <link.icon className="w-4 h-4 text-white/30 group-hover:text-white/60" />
              <span className="text-sm">{link.label}</span>
              <ExternalLink className="w-3 h-3 ml-auto text-white/20 group-hover:text-white/40" />
            </a>
          ))}
        </div>
      </nav>

      {/* Bottom status */}
      <div className="p-4 border-t border-white/8">
        <div className="glass-card p-3">
          <div className="flex items-center gap-2 mb-2">
            <div className="dot-live" />
            <span className="text-xs font-semibold text-white/80">System Operational</span>
          </div>
          <div className="space-y-1">
            {[
              { label: "API", status: "online", color: "text-safe" },
              { label: "ML Model", status: "loaded", color: "text-safe" },
              { label: "DB", status: "connected", color: "text-safe" },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <span className="text-xs text-white/40 font-mono">{item.label}</span>
                <span className={`text-xs font-mono ${item.color}`}>{item.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}
