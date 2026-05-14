"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, Award, Clock, Tag, BarChart2, ArrowUpCircle, CheckCircle } from "lucide-react";
import { clsx } from "clsx";
import toast from "react-hot-toast";

const MOCK_MODELS = [
  {
    name: "fraudshield_classifier",
    version: "3",
    stage: "Production",
    modelType: "XGBoost",
    runId: "abc123def456",
    f1: 0.9124,
    aucPr: 0.9341,
    rocAuc: 0.9812,
    precision: 0.8967,
    recall: 0.9289,
    createdAt: "2024-03-15 10:23",
    description: "XGBoost trained on 100k synthetic transactions with SMOTE",
  },
  {
    name: "fraudshield_classifier",
    version: "2",
    stage: "Staging",
    modelType: "LightGBM",
    runId: "xyz789ghi012",
    f1: 0.8991,
    aucPr: 0.9187,
    rocAuc: 0.9743,
    precision: 0.8823,
    recall: 0.9167,
    createdAt: "2024-03-10 08:15",
    description: "LightGBM challenger model with early stopping",
  },
  {
    name: "fraudshield_classifier",
    version: "1",
    stage: "Archived",
    modelType: "XGBoost",
    runId: "prev123model456",
    f1: 0.8534,
    aucPr: 0.8721,
    rocAuc: 0.9456,
    precision: 0.8312,
    recall: 0.8764,
    createdAt: "2024-03-01 14:00",
    description: "Initial XGBoost baseline model",
  },
];

const STAGE_CONFIG: Record<string, { color: string; bg: string; border: string }> = {
  Production: { color: "#00D68F", bg: "rgba(0,214,143,0.1)", border: "rgba(0,214,143,0.25)" },
  Staging: { color: "#FFB800", bg: "rgba(255,184,0,0.1)", border: "rgba(255,184,0,0.25)" },
  Archived: { color: "rgba(255,255,255,0.3)", bg: "rgba(255,255,255,0.04)", border: "rgba(255,255,255,0.08)" },
};

function MetricBar({ value, max = 1, color }: { value: number; max?: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${(value / max) * 100}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="h-full rounded-full"
          style={{ background: color }}
        />
      </div>
      <span className="text-xs font-mono w-12 text-right" style={{ color }}>
        {(value * 100).toFixed(1)}%
      </span>
    </div>
  );
}

export default function ModelsPage() {
  const [selected, setSelected] = useState(MOCK_MODELS[0]);
  const [promoting, setPromoting] = useState(false);

  const handlePromote = async (version: string) => {
    setPromoting(true);
    await new Promise((r) => setTimeout(r, 1500));
    setPromoting(false);
    toast.success(`Model v${version} promoted to Production!`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Model <span className="text-neon-cyan">Registry</span></h1>
        <p className="text-sm text-white/40 mt-0.5">Manage MLflow model versions and promote champions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model list */}
        <div className="space-y-3">
          {MOCK_MODELS.map((model, i) => {
            const stageConfig = STAGE_CONFIG[model.stage];
            const isSelected = selected.version === model.version;

            return (
              <motion.div
                key={model.version}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                onClick={() => setSelected(model)}
                className={clsx(
                  "glass-card p-4 cursor-pointer transition-all duration-200",
                  isSelected && "border-cyan-neon/30"
                )}
                style={isSelected ? {
                  background: "rgba(0,245,255,0.06)",
                  borderColor: "rgba(0,245,255,0.25)",
                } : {}}
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <BrainCircuit className="w-4 h-4 text-cyan-neon" />
                      <span className="text-sm font-semibold text-white">{model.modelType}</span>
                      <span className="text-xs font-mono text-white/40">v{model.version}</span>
                    </div>
                    <p className="text-xs text-white/30 mt-0.5 font-mono">{model.runId.slice(0, 12)}...</p>
                  </div>
                  <span
                    className="text-xs font-semibold px-2 py-0.5 rounded-full"
                    style={{ color: stageConfig.color, background: stageConfig.bg, border: `1px solid ${stageConfig.border}` }}
                  >
                    {model.stage}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs font-mono text-white/40">
                  <span>F1: <span className="text-white/80">{(model.f1 * 100).toFixed(1)}%</span></span>
                  <span>AUC: <span className="text-white/80">{(model.aucPr * 100).toFixed(1)}%</span></span>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Model detail */}
        <div className="lg:col-span-2 space-y-4">
          <div className="glass-card p-5">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white">{selected.modelType} Classifier</h2>
                <p className="text-sm text-white/40">Version {selected.version} · {selected.description}</p>
              </div>
              {selected.stage !== "Production" && (
                <button
                  onClick={() => handlePromote(selected.version)}
                  disabled={promoting}
                  className="btn-primary flex items-center gap-2"
                >
                  <ArrowUpCircle className="w-4 h-4" />
                  {promoting ? "Promoting..." : "Promote to Production"}
                </button>
              )}
              {selected.stage === "Production" && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-safe/10 border border-safe/20">
                  <CheckCircle className="w-4 h-4 text-safe" />
                  <span className="text-sm font-semibold text-safe">Champion Model</span>
                </div>
              )}
            </div>

            {/* Metrics */}
            <div className="space-y-3">
              <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wider">Performance Metrics</h3>
              {[
                { label: "F1 Score", value: selected.f1, color: "#00F5FF" },
                { label: "AUC-PR", value: selected.aucPr, color: "#7C3AED" },
                { label: "ROC-AUC", value: selected.rocAuc, color: "#00D68F" },
                { label: "Precision", value: selected.precision, color: "#FFB800" },
                { label: "Recall", value: selected.recall, color: "#a855f7" },
              ].map((m) => (
                <div key={m.label} className="flex items-center gap-3">
                  <span className="text-xs text-white/50 w-24">{m.label}</span>
                  <div className="flex-1">
                    <MetricBar value={m.value} color={m.color} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* MLflow info */}
          <div className="glass-card p-4">
            <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-3">Run Details</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: "Run ID", value: selected.runId },
                { label: "Model Type", value: selected.modelType },
                { label: "Stage", value: selected.stage },
                { label: "Created", value: selected.createdAt },
                { label: "Registry", value: selected.name },
                { label: "Threshold", value: "0.50" },
              ].map((item) => (
                <div key={item.label} className="bg-white/3 rounded-lg p-2.5">
                  <p className="text-xs text-white/30">{item.label}</p>
                  <p className="text-sm font-mono text-white/80 mt-0.5">{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
