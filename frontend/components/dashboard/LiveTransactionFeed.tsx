"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, CheckCircle, Clock, CreditCard } from "lucide-react";
import { clsx } from "clsx";

const MERCHANT_CATEGORIES = [
  "Grocery", "Restaurant", "Gas Station", "Online Retail",
  "Travel", "Electronics", "Pharmacy", "Clothing",
];
const CARD_TYPES = ["Visa", "Mastercard", "Amex", "Discover"];
const COUNTRIES = ["US", "GB", "CA", "AU", "DE", "FR"];

function generateTransaction() {
  const isFraud = Math.random() < 0.025;
  const amount = isFraud
    ? Math.random() < 0.3
      ? +(Math.random() * 4 + 0.01).toFixed(2)
      : +(Math.random() * 4800 + 200).toFixed(2)
    : +(Math.random() * 495 + 5).toFixed(2);

  const fraudProb = isFraud
    ? +(Math.random() * 0.34 + 0.66).toFixed(3)
    : +(Math.random() * 0.35).toFixed(3);

  return {
    id: `TXN_${Math.floor(Math.random() * 1e9).toString().padStart(9, "0")}`,
    amount,
    category: MERCHANT_CATEGORIES[Math.floor(Math.random() * MERCHANT_CATEGORIES.length)],
    cardType: CARD_TYPES[Math.floor(Math.random() * CARD_TYPES.length)],
    country: COUNTRIES[Math.floor(Math.random() * COUNTRIES.length)],
    isFraud,
    fraudProb,
    riskLevel: fraudProb >= 0.8 ? "HIGH" : fraudProb >= 0.5 ? "MEDIUM" : "LOW",
    timestamp: new Date().toLocaleTimeString("en-US", { hour12: false }),
  };
}

export default function LiveTransactionFeed() {
  const [transactions, setTransactions] = useState(() =>
    Array.from({ length: 8 }, generateTransaction)
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setTransactions((prev) => [generateTransaction(), ...prev.slice(0, 14)]);
    }, 800 + Math.random() * 1200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-card p-4 h-[380px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-white/80">Live Transaction Feed</h2>
          <div className="dot-live" />
        </div>
        <span className="text-xs text-white/30 font-mono">
          {transactions.length} events
        </span>
      </div>

      <div className="flex-1 overflow-hidden">
        <table className="w-full data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Category</th>
              <th>Amount</th>
              <th>Risk</th>
              <th>Prob</th>
              <th>Status</th>
            </tr>
          </thead>
        </table>

        <div className="overflow-y-auto" style={{ maxHeight: "280px" }}>
          <table className="w-full data-table">
            <tbody>
              <AnimatePresence initial={false}>
                {transactions.map((txn) => (
                  <motion.tr
                    key={txn.id}
                    initial={{ opacity: 0, x: 20, backgroundColor: txn.isFraud ? "rgba(255,45,85,0.1)" : "rgba(0,245,255,0.05)" }}
                    animate={{ opacity: 1, x: 0, backgroundColor: "transparent" }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="hover:bg-white/3 transition-colors"
                  >
                    <td>
                      <span className="text-xs font-mono text-white/40">
                        {txn.id.slice(-8)}
                      </span>
                    </td>
                    <td>
                      <span className="text-xs text-white/70">{txn.category}</span>
                    </td>
                    <td>
                      <span className="text-xs font-mono font-semibold text-white/90">
                        ${txn.amount.toLocaleString()}
                      </span>
                    </td>
                    <td>
                      <span className={clsx(
                        "text-xs font-mono font-semibold",
                        txn.riskLevel === "HIGH" ? "text-fraud" :
                        txn.riskLevel === "MEDIUM" ? "text-warning" : "text-safe"
                      )}>
                        {txn.riskLevel}
                      </span>
                    </td>
                    <td>
                      <span className={clsx(
                        "text-xs font-mono",
                        txn.fraudProb >= 0.5 ? "text-fraud" : "text-white/50"
                      )}>
                        {(txn.fraudProb * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td>
                      {txn.isFraud ? (
                        <span className="badge-fraud">
                          <AlertTriangle className="w-3 h-3" />
                          Fraud
                        </span>
                      ) : (
                        <span className="badge-safe">
                          <CheckCircle className="w-3 h-3" />
                          Clean
                        </span>
                      )}
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
