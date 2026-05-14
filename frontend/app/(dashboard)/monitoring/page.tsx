"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Activity, AlertTriangle, CheckCircle, TrendingUp, ExternalLink } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const DRIFT_FEATURES = [
  { feature: "distance_from_home", score: 0.38, drifted: true },
  { feature: "transaction_count_1h", score: 0.09, drifted: false },
  { feature: "velocity_score", score: 0.11, drifted: false },
  { feature: "amount", score: 0.04, drifted: false },
  { feature: "merchant_risk_score", score: 0.06, drifted: false },
  { feature: "amount_mean_1h", score: 0.07, drifted: false },
];

function genDriftHistory() {
  return Array.from({ length: 14 }, (_, i) => {
    const d = new Date(); d.setDate(d.getDate() - 13 + i);
    return {
      date: d.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      drift_share: +(Math.random() * 0.15 + 0.02).toFixed(3),
      n_drifted: Math.floor(Math.random() * 3),
    };
  });
}

export default function MonitoringPage() {
  const [driftHistory] = useState(genDriftHistory);
  const [modelMetrics, setModelMetrics] = useState({ latency_p50: 14.2, latency_p99: 48.7, requests_per_min: 1847, error_rate: 0.002 });

  useEffect(() => {
    const interval = setInterval(() => {
      setModelMetrics(prev => ({
        latency_p50: +(prev.latency_p50 + (Math.random() - 0.5) * 2).toFixed(1),
        latency_p99: +(prev.latency_p99 + (Math.random() - 0.5) * 5).toFixed(1),
        requests_per_min: prev.requests_per_min + Math.floor((Math.random() - 0.5) * 100),
        error_rate: +Math.max(0, prev.error_rate + (Math.random() - 0.5) * 0.001).toFixed(4),
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Drift <span className="text-neon-cyan">Monitoring</span></h1>
          <p className="text-sm text-white/40 mt-0.5">Evidently AI drift detection · Grafana metrics</p>
        </div>
        <a href="http://localhost:3001" target="_blank" rel="noopener noreferrer"
          className="glass-btn flex items-center gap-2 text-white/60">
          <ExternalLink className="w-4 h-4" /> Open Grafana
        </a>
      </div>

      {/* Status banner */}
      <div className="glass-card p-4 border border-safe/20"
        style={{ background: "rgba(0,214,143,0.05)" }}>
        <div className="flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-safe" />
          <div>
            <p className="text-sm font-semibold text-safe">No Significant Drift Detected</p>
            <p className="text-xs text-white/40">Drift share: 8% · 1 feature flagged · Last check: 2 minutes ago</p>
          </div>
        </div>
      </div>

      {/* Live metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Latency P50", value: `${modelMetrics.latency_p50}ms`, color: "#00F5FF" },
          { label: "Latency P99", value: `${modelMetrics.latency_p99}ms`, color: "#FFB800" },
          { label: "Req/min", value: modelMetrics.requests_per_min.toLocaleString(), color: "#00D68F" },
          { label: "Error Rate", value: `${(modelMetrics.error_rate * 100).toFixed(2)}%`, color: "#FF2D55" },
        ].map((item, i) => (
          <motion.div key={item.label} className="glass-card p-4">
            <p className="text-xs text-white/40">{item.label}</p>
            <motion.p key={item.value} initial={{ opacity: 0.6 }} animate={{ opacity: 1 }}
              className="text-xl font-bold font-mono mt-1" style={{ color: item.color }}>{item.value}</motion.p>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Drift history chart */}
        <div className="glass-card p-4">
          <h2 className="text-sm font-semibold text-white/80 mb-4">14-Day Drift Share History</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={driftHistory} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: "rgba(255,255,255,0.3)" }} tickLine={false} interval={2} />
              <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} tickLine={false} axisLine={false} tickFormatter={v => `${(v*100).toFixed(0)}%`} />
              <Tooltip contentStyle={{ background: "rgba(8,14,31,0.95)", border: "1px solid rgba(0,245,255,0.2)", borderRadius: "12px", color: "white" }} formatter={(v: any) => [`${(v*100).toFixed(1)}%`, "Drift Share"]} />
              <Line type="monotone" dataKey="drift_share" stroke="#00F5FF" strokeWidth={2} dot={{ fill: "#00F5FF", r: 3 }} />
              {/* Threshold line at 30% */}
              <Line type="monotone" data={driftHistory.map(d => ({ ...d, threshold: 0.3 }))} dataKey="threshold"
                stroke="#FF2D55" strokeWidth={1} strokeDasharray="4 4" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Feature drift scores */}
        <div className="glass-card p-4">
          <h2 className="text-sm font-semibold text-white/80 mb-4">Feature Drift Scores (PSI)</h2>
          <div className="space-y-3">
            {DRIFT_FEATURES.map((feat) => (
              <div key={feat.feature} className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-white/60">{feat.feature}</span>
                    <span className={`text-xs font-semibold font-mono ${feat.drifted ? "text-fraud" : "text-safe"}`}>
                      {feat.score.toFixed(2)}
                    </span>
                  </div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${Math.min(feat.score / 0.5 * 100, 100)}%` }}
                      transition={{ duration: 1 }}
                      className="h-full rounded-full"
                      style={{ background: feat.drifted ? "#FF2D55" : "#00D68F" }} />
                  </div>
                </div>
                {feat.drifted && <AlertTriangle className="w-4 h-4 text-fraud flex-shrink-0" />}
              </div>
            ))}
          </div>
          <div className="mt-3 pt-3 border-t border-white/8 flex items-center justify-between text-xs text-white/30">
            <span>Threshold: PSI &gt; 0.3</span>
            <span className="text-fraud font-mono">1 / {DRIFT_FEATURES.length} drifted</span>
          </div>
        </div>
      </div>
    </div>
  );
}
