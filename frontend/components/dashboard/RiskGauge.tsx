"use client";

import { useMemo } from "react";

interface RiskGaugeProps {
  value: number; // 0-100
  label?: string;
}

export default function RiskGauge({ value, label = "F1 Score" }: RiskGaugeProps) {
  const radius = 54;
  const strokeWidth = 8;
  const circumference = 2 * Math.PI * radius;
  // Only use top 180° (semicircle)
  const arc = circumference * 0.75;
  const dashOffset = arc - (arc * value) / 100;

  const color =
    value >= 90 ? "#00D68F" :
    value >= 75 ? "#FFB800" :
    "#FF2D55";

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-36 h-36">
        <svg
          viewBox="0 0 128 128"
          className="w-full h-full -rotate-[135deg]"
        >
          {/* Track */}
          <circle
            cx="64" cy="64" r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={strokeWidth}
            strokeDasharray={`${arc} ${circumference}`}
            strokeLinecap="round"
          />
          {/* Fill */}
          <circle
            cx="64" cy="64" r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${arc} ${circumference}`}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            style={{
              transition: "stroke-dashoffset 1.2s ease, stroke 0.5s ease",
              filter: `drop-shadow(0 0 6px ${color})`,
            }}
          />
        </svg>
        {/* Value label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center mt-4">
          <span className="text-2xl font-bold" style={{ color }}>
            {value.toFixed(1)}%
          </span>
          <span className="text-xs text-white/40 font-mono">{label}</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex gap-4 mt-2">
        {[
          { label: "High", color: "#00D68F", threshold: "≥90%" },
          { label: "Med", color: "#FFB800", threshold: "≥75%" },
          { label: "Low", color: "#FF2D55", threshold: "<75%" },
        ].map((item) => (
          <div key={item.label} className="flex flex-col items-center gap-1">
            <div className="w-2 h-2 rounded-full" style={{ background: item.color }} />
            <span className="text-xs text-white/30 font-mono">{item.threshold}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
