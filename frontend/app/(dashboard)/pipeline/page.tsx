"use client";

import { motion } from "framer-motion";
import { CheckCircle, Clock, AlertTriangle, Play } from "lucide-react";

const PIPELINE_STAGES = [
  { id: "ingest", label: "Data Ingestion", status: "success", duration: "12.4s", time: "02:00 UTC" },
  { id: "validate", label: "GE Validation", status: "success", duration: "4.1s", time: "02:00 UTC" },
  { id: "preprocess", label: "Preprocessing", status: "success", duration: "28.7s", time: "02:01 UTC" },
  { id: "train", label: "Model Training", status: "success", duration: "4m 32s", time: "02:01 UTC" },
  { id: "evaluate", label: "Evaluation", status: "success", duration: "18.3s", time: "02:05 UTC" },
  { id: "register", label: "Model Registry", status: "success", duration: "2.1s", time: "02:06 UTC" },
  { id: "drift", label: "Drift Monitor", status: "running", duration: "—", time: "02:06 UTC" },
];

const DAGS = [
  { name: "fraud_training_pipeline", schedule: "Weekly Mon 02:00", lastRun: "2024-03-18 02:00", status: "success", duration: "5m 37s" },
  { name: "data_ingestion_pipeline", schedule: "Daily 06:00", lastRun: "2024-03-18 06:00", status: "success", duration: "23s" },
  { name: "drift_monitoring_pipeline", schedule: "Daily 08:00", lastRun: "2024-03-18 08:00", status: "running", duration: "—" },
];

const STATUS_CFG: Record<string, { icon: any; color: string; bg: string; label: string }> = {
  success: { icon: CheckCircle, color: "#00D68F", bg: "rgba(0,214,143,0.1)", label: "Success" },
  running: { icon: Clock, color: "#00F5FF", bg: "rgba(0,245,255,0.1)", label: "Running" },
  failed: { icon: AlertTriangle, color: "#FF2D55", bg: "rgba(255,45,85,0.1)", label: "Failed" },
};

export default function PipelinePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">ML <span className="text-neon-cyan">Pipeline</span></h1>
          <p className="text-sm text-white/40 mt-0.5">Airflow DAG status · DVC pipeline stages</p>
        </div>
        <button className="btn-primary flex items-center gap-2"><Play className="w-4 h-4" /> Trigger Run</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {DAGS.map((dag, i) => {
          const cfg = STATUS_CFG[dag.status] || STATUS_CFG.success;
          const Icon = cfg.icon;
          return (
            <motion.div key={dag.name} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              className="glass-card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-white/30">{dag.schedule}</span>
                <span className="flex items-center gap-1.5 text-xs font-semibold px-2 py-0.5 rounded-full"
                  style={{ color: cfg.color, background: cfg.bg }}>
                  <Icon className="w-3 h-3" />{cfg.label}
                </span>
              </div>
              <p className="text-sm font-semibold text-white/90 font-mono">{dag.name}</p>
              <p className="text-xs text-white/30 mt-1">Last: {dag.lastRun} · <span className="text-cyan-neon">{dag.duration}</span></p>
            </motion.div>
          );
        })}
      </div>

      <div className="glass-card p-5">
        <h2 className="text-sm font-semibold text-white/80 mb-5">Training Pipeline Stages</h2>
        <div className="relative">
          <div className="absolute left-[19px] top-5 bottom-5 w-0.5 bg-white/8" />
          <div className="space-y-3">
            {PIPELINE_STAGES.map((stage, i) => {
              const cfg = STATUS_CFG[stage.status] || STATUS_CFG.success;
              const Icon = cfg.icon;
              return (
                <motion.div key={stage.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.07 }}
                  className="flex items-center gap-4 relative">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 z-10"
                    style={{ background: cfg.bg, border: `1px solid ${cfg.color}30` }}>
                    <Icon className={`w-4 h-4 ${stage.status === "running" ? "animate-spin" : ""}`} style={{ color: cfg.color }} />
                  </div>
                  <div className="flex-1 flex items-center justify-between py-2 px-3 rounded-xl bg-white/2 border border-white/5">
                    <div>
                      <p className="text-sm font-semibold text-white/90">{stage.label}</p>
                      <p className="text-xs text-white/30 font-mono">{stage.time}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-mono font-semibold" style={{ color: cfg.color }}>{cfg.label}</p>
                      <p className="text-xs text-white/30 font-mono">{stage.duration}</p>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
