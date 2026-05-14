"use client";

import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import {
  TrendingUp, TrendingDown, AlertTriangle, Shield,
  DollarSign, Zap, Activity, Clock,
} from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import dynamic from "next/dynamic";
import LiveTransactionFeed from "@/components/dashboard/LiveTransactionFeed";
import MetricCard from "@/components/dashboard/MetricCard";
import RiskGauge from "@/components/dashboard/RiskGauge";

// Lazy-load Three.js scene to avoid SSR issues
const CyberGlobe = dynamic(() => import("@/components/three/CyberGlobe"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center">
      <div className="w-16 h-16 border-2 border-cyan-neon/30 border-t-cyan-neon rounded-full animate-spin" />
    </div>
  ),
});

// Mock analytics data
function generateTrendData() {
  return Array.from({ length: 24 }, (_, h) => ({
    hour: `${h.toString().padStart(2, "0")}:00`,
    transactions: Math.floor(Math.random() * 3000 + 1000),
    fraud: Math.floor(Math.random() * 60 + 20),
    fraudRate: +(Math.random() * 0.03 + 0.015).toFixed(4),
  }));
}

const CATEGORY_DATA = [
  { name: "Online Retail", fraudRate: 4.8, color: "#FF2D55" },
  { name: "Electronics", fraudRate: 4.2, color: "#FF6B6B" },
  { name: "ATM", fraudRate: 3.8, color: "#FFB800" },
  { name: "Travel", fraudRate: 3.1, color: "#FFB800" },
  { name: "Gas Station", fraudRate: 1.9, color: "#00D68F" },
  { name: "Grocery", fraudRate: 0.8, color: "#00D68F" },
];

export default function DashboardPage() {
  const [trendData] = useState(generateTrendData);
  const [metrics, setMetrics] = useState({
    totalTransactions: 47832,
    fraudDetected: 1004,
    fraudRate: 2.1,
    blocked: 892,
    reviewQueue: 112,
    accuracy: 91.24,
    modelLatency: 14.3,
  });

  // Animate metrics counter
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        ...prev,
        totalTransactions: prev.totalTransactions + Math.floor(Math.random() * 5),
        fraudDetected: prev.fraudDetected + (Math.random() < 0.05 ? 1 : 0),
      }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Fraud Detection{" "}
            <span className="text-neon-cyan">Overview</span>
          </h1>
          <p className="text-sm text-white/40 mt-0.5">
            Real-time monitoring · XGBoost Production Model v3
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="dot-live" />
          <span className="text-xs text-white/50 font-mono">LIVE</span>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Total Transactions"
          value={metrics.totalTransactions.toLocaleString()}
          change="+12.4%"
          positive
          icon={<Activity className="w-4 h-4" />}
          color="cyan"
        />
        <MetricCard
          label="Fraud Detected"
          value={metrics.fraudDetected.toLocaleString()}
          change="+3.2%"
          positive={false}
          icon={<AlertTriangle className="w-4 h-4" />}
          color="fraud"
        />
        <MetricCard
          label="Fraud Rate"
          value={`${metrics.fraudRate.toFixed(2)}%`}
          change="-0.1%"
          positive
          icon={<TrendingDown className="w-4 h-4" />}
          color="warning"
        />
        <MetricCard
          label="Model F1 Score"
          value={`${metrics.accuracy.toFixed(2)}%`}
          change="+0.8%"
          positive
          icon={<Shield className="w-4 h-4" />}
          color="safe"
        />
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D Globe */}
        <div className="lg:col-span-1">
          <div className="glass-card h-72 p-4 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-semibold text-white/80">Global Fraud Map</h2>
              <span className="badge-fraud">
                <span className="w-1.5 h-1.5 rounded-full bg-fraud animate-pulse" />
                Live
              </span>
            </div>
            <div className="flex-1 rounded-xl overflow-hidden">
              <CyberGlobe />
            </div>
          </div>
        </div>

        {/* Hourly Trend Chart */}
        <div className="lg:col-span-2">
          <div className="glass-card h-72 p-4 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-white/80">24-Hour Fraud Trend</h2>
              <div className="flex gap-4 text-xs text-white/40">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-cyan-neon" />
                  Transactions
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-fraud" />
                  Fraud
                </span>
              </div>
            </div>
            <div className="flex-1">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="gradCyan" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00F5FF" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#00F5FF" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gradFraud" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FF2D55" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#FF2D55" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="hour" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      background: "rgba(8,14,31,0.95)",
                      border: "1px solid rgba(0,245,255,0.2)",
                      borderRadius: "12px",
                      color: "white",
                    }}
                  />
                  <Area
                    type="monotone" dataKey="transactions"
                    stroke="#00F5FF" strokeWidth={2}
                    fill="url(#gradCyan)" dot={false}
                  />
                  <Area
                    type="monotone" dataKey="fraud"
                    stroke="#FF2D55" strokeWidth={2}
                    fill="url(#gradFraud)" dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live feed */}
        <div className="lg:col-span-2">
          <LiveTransactionFeed />
        </div>

        {/* Category bar + gauge */}
        <div className="flex flex-col gap-4">
          {/* Risk gauge */}
          <div className="glass-card p-4">
            <h2 className="text-sm font-semibold text-white/80 mb-3">Model Confidence</h2>
            <RiskGauge value={91.24} />
          </div>

          {/* Category fraud rates */}
          <div className="glass-card p-4 flex-1">
            <h2 className="text-sm font-semibold text-white/80 mb-3">Fraud Rate by Category</h2>
            <div className="space-y-2">
              {CATEGORY_DATA.map((item) => (
                <div key={item.name} className="flex items-center gap-3">
                  <span className="text-xs text-white/50 w-24 truncate font-mono">{item.name}</span>
                  <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(item.fraudRate / 5) * 100}%` }}
                      transition={{ duration: 1, delay: 0.2 }}
                      className="h-full rounded-full"
                      style={{ background: item.color }}
                    />
                  </div>
                  <span className="text-xs font-mono font-semibold w-10 text-right"
                    style={{ color: item.color }}>
                    {item.fraudRate}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
