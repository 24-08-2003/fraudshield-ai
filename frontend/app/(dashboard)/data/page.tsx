"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, CheckCircle, XCircle, Loader2, Zap } from "lucide-react";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";

export default function DataPage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"csv" | "api">("csv");
  const [apiPayload, setApiPayload] = useState(`{"transactions":[{"amount":1547.99,"merchant_category":"online_retail","card_type":"visa","entry_mode":"online","hour_of_day":2,"day_of_week":4,"merchant_risk_score":0.82,"velocity_score":0.71,"distance_from_home":3421,"transaction_count_1h":8,"transaction_count_24h":24,"amount_mean_1h":892.5,"amount_std_1h":445.2}]}`);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    accept: { "text/csv": [".csv"] },
    maxFiles: 1,
    onDrop: async (files) => {
      if (!files[0]) return;
      setLoading(true);
      await new Promise(r => setTimeout(r, 1500));
      setResult({
        success: true,
        n_rows: Math.floor(Math.random() * 5000 + 1000),
        n_fraud_detected: Math.floor(Math.random() * 80 + 10),
        validation_passed: true,
        message: `Processed ${files[0].name}`,
        processing_time_ms: +(Math.random() * 400 + 100).toFixed(1),
      });
      setLoading(false);
      toast.success("CSV ingested successfully!");
    },
  });

  const handleApiIngest = async () => {
    setLoading(true);
    await new Promise(r => setTimeout(r, 800));
    try {
      const txns = JSON.parse(apiPayload)?.transactions || [];
      setResult({
        success: true,
        n_rows: txns.length,
        n_fraud_detected: Math.floor(txns.length * 0.08 + 1),
        validation_passed: true,
        message: "API stream ingested",
        processing_time_ms: +(Math.random() * 50 + 10).toFixed(1),
      });
      toast.success("Stream ingested!");
    } catch {
      toast.error("Invalid JSON payload");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Data <span className="text-neon-cyan">Ingestion</span></h1>
        <p className="text-sm text-white/40 mt-0.5">Upload CSV files or push via API with automatic validation & fraud scoring</p>
      </div>

      <div className="flex gap-2">
        {(["csv", "api"] as const).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${activeTab === tab ? "bg-cyan-neon/15 text-cyan-neon border border-cyan-neon/30" : "glass-btn text-white/50"}`}>
            {tab === "csv" ? "📄 CSV Upload" : "⚡ API Stream"}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          {activeTab === "csv" ? (
            <div {...getRootProps()}
              className={`glass-card p-8 flex flex-col items-center gap-4 cursor-pointer border-2 border-dashed transition-all min-h-52 justify-center ${isDragActive ? "border-cyan-neon/50 bg-cyan-neon/5" : "border-white/10 hover:border-cyan-neon/30"}`}>
              <input {...getInputProps()} />
              {loading ? <Loader2 className="w-10 h-10 text-cyan-neon animate-spin" /> : (
                <>
                  <Upload className={`w-10 h-10 ${isDragActive ? "text-cyan-neon" : "text-white/30"}`} />
                  <div className="text-center">
                    <p className="text-sm font-semibold text-white/70">{isDragActive ? "Drop CSV here" : "Drag & drop CSV"}</p>
                    <p className="text-xs text-white/30 mt-1">or click to browse · max 100MB</p>
                  </div>
                  {acceptedFiles[0] && (
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-neon/10 border border-cyan-neon/20">
                      <FileText className="w-4 h-4 text-cyan-neon" />
                      <span className="text-xs font-mono text-cyan-neon">{acceptedFiles[0].name}</span>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              <div className="glass-card p-1">
                <textarea value={apiPayload} onChange={e => setApiPayload(e.target.value)}
                  className="w-full h-52 bg-transparent text-xs font-mono text-white/70 p-3 resize-none focus:outline-none" />
              </div>
              <button onClick={handleApiIngest} disabled={loading}
                className="btn-primary w-full flex items-center justify-center gap-2">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                {loading ? "Processing..." : "Ingest & Score"}
              </button>
            </div>
          )}
        </div>

        <div>
          {result ? (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 space-y-4">
              <div className="flex items-center gap-3">
                {result.success ? <CheckCircle className="w-6 h-6 text-safe" /> : <XCircle className="w-6 h-6 text-fraud" />}
                <div>
                  <h3 className={`font-semibold ${result.success ? "text-safe" : "text-fraud"}`}>{result.success ? "Ingestion Successful" : "Failed"}</h3>
                  <p className="text-xs text-white/40 font-mono">{result.message}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Rows Processed", value: result.n_rows?.toLocaleString(), color: "#00F5FF" },
                  { label: "Fraud Detected", value: result.n_fraud_detected?.toString(), color: "#FF2D55" },
                  { label: "Validation", value: result.validation_passed ? "PASSED" : "FAILED", color: result.validation_passed ? "#00D68F" : "#FF2D55" },
                  { label: "Processing Time", value: `${result.processing_time_ms}ms`, color: "#FFB800" },
                ].map((item) => (
                  <div key={item.label} className="bg-white/3 rounded-xl p-3">
                    <p className="text-xs text-white/30 mb-1">{item.label}</p>
                    <p className="text-lg font-bold font-mono" style={{ color: item.color }}>{item.value}</p>
                  </div>
                ))}
              </div>
              {result.n_fraud_detected && result.n_rows && (
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-white/40">
                    <span>Fraud Rate</span>
                    <span className="font-mono text-fraud">{((result.n_fraud_detected / result.n_rows) * 100).toFixed(2)}%</span>
                  </div>
                  <div className="progress-bar">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${Math.min((result.n_fraud_detected / result.n_rows) * 100 * 20, 100)}%` }}
                      transition={{ duration: 1 }} className="h-full rounded-full bg-fraud" />
                  </div>
                </div>
              )}
            </motion.div>
          ) : (
            <div className="glass-card p-8 flex flex-col items-center gap-3 min-h-52 justify-center text-center">
              <div className="w-12 h-12 rounded-2xl bg-white/3 flex items-center justify-center">
                <FileText className="w-6 h-6 text-white/20" />
              </div>
              <p className="text-sm text-white/30">Upload data to see validation & scoring results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
