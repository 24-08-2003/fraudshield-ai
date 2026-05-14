"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

function genDailyData() {
  return Array.from({ length: 30 }, (_, i) => {
    const d = new Date(); d.setDate(d.getDate() - 29 + i);
    const txns = Math.floor(Math.random() * 30000 + 15000);
    const fraud = Math.floor(txns * (0.018 + Math.random() * 0.008));
    return { date: d.toLocaleDateString("en-US", { month: "short", day: "numeric" }), transactions: txns, fraud, fraudRate: +(fraud / txns * 100).toFixed(2) };
  });
}

const CATEGORY_DATA = [
  { name: "Online Retail", fraud: 4.8 }, { name: "Electronics", fraud: 4.2 },
  { name: "ATM", fraud: 3.8 }, { name: "Travel", fraud: 3.1 },
  { name: "Gas", fraud: 1.9 }, { name: "Restaurant", fraud: 1.1 },
  { name: "Grocery", fraud: 0.8 }, { name: "Pharmacy", fraud: 0.6 },
];

const AMOUNT_DATA = [
  { range: "$0-50", legitimate: 28450, fraud: 234 },
  { range: "$50-200", legitimate: 18900, fraud: 445 },
  { range: "$200-500", legitimate: 9800, fraud: 567 },
  { range: "$500-1k", legitimate: 4500, fraud: 389 },
  { range: "$1k+", legitimate: 2100, fraud: 312 },
];

export default function AnalyticsPage() {
  const [dailyData] = useState(genDailyData);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Fraud <span className="text-neon-cyan">Analytics</span></h1>
        <p className="text-sm text-white/40 mt-0.5">30-day trends, category breakdown, and amount distribution</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Avg Daily Fraud", value: "668 txns", color: "#FF2D55" },
          { label: "Peak Fraud Rate", value: "3.24%", color: "#FFB800" },
          { label: "Highest Risk", value: "Online Retail", color: "#a855f7" },
          { label: "Fraud Prevented", value: "$1.2M", color: "#00D68F" },
        ].map((item, i) => (
          <motion.div key={item.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
            className="glass-card p-4">
            <p className="text-xs text-white/40">{item.label}</p>
            <p className="text-xl font-bold mt-1" style={{ color: item.color }}>{item.value}</p>
          </motion.div>
        ))}
      </div>

      <div className="glass-card p-4">
        <h2 className="text-sm font-semibold text-white/80 mb-4">30-Day Fraud Rate Trend</h2>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={dailyData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="gFraud" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FF2D55" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#FF2D55" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tick={{ fontSize: 9, fill: "rgba(255,255,255,0.3)" }} tickLine={false} interval={4} />
            <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: "rgba(8,14,31,0.95)", border: "1px solid rgba(255,45,85,0.3)", borderRadius: "12px", color: "white" }} />
            <Area type="monotone" dataKey="fraudRate" stroke="#FF2D55" strokeWidth={2} fill="url(#gFraud)" dot={false} name="Fraud Rate %" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-4">
          <h2 className="text-sm font-semibold text-white/80 mb-4">Fraud Rate by Merchant Category</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={CATEGORY_DATA} layout="vertical" margin={{ left: 20, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} tickFormatter={(v) => `${v}%`} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.4)" }} width={80} />
              <Tooltip contentStyle={{ background: "rgba(8,14,31,0.95)", border: "1px solid rgba(0,245,255,0.2)", borderRadius: "12px", color: "white" }} formatter={(v) => [`${v}%`, "Fraud Rate"]} />
              <Bar dataKey="fraud" radius={[0, 4, 4, 0]} fill="#FF2D55" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card p-4">
          <h2 className="text-sm font-semibold text-white/80 mb-4">Fraud vs Legitimate by Amount Range</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={AMOUNT_DATA} margin={{ top: 5, right: 5, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="range" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: "rgba(8,14,31,0.95)", border: "1px solid rgba(0,245,255,0.2)", borderRadius: "12px", color: "white" }} />
              <Bar dataKey="legitimate" fill="rgba(0,245,255,0.3)" radius={[4, 4, 0, 0]} name="Legitimate" />
              <Bar dataKey="fraud" fill="#FF2D55" radius={[4, 4, 0, 0]} name="Fraud" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
