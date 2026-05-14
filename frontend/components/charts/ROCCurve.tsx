'use client';

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';

interface ROCPoint { fpr: number; tpr: number; }
interface ROCCurveProps { data: ROCPoint[]; }

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(5,8,19,0.95)',
      border: '1px solid rgba(0,245,255,0.2)',
      borderRadius: 10,
      padding: '10px 14px',
      fontSize: 13,
    }}>
      <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11, marginBottom: 4 }}>Operating Point</div>
      <div style={{ color: 'var(--cyan)', fontFamily: 'JetBrains Mono, monospace' }}>
        TPR: {payload[0]?.payload?.tpr?.toFixed(4)}
      </div>
      <div style={{ color: '#FF2D55', fontFamily: 'JetBrains Mono, monospace' }}>
        FPR: {payload[0]?.payload?.fpr?.toFixed(4)}
      </div>
    </div>
  );
};

export default function ROCCurve({ data }: ROCCurveProps) {
  // Add baseline (random classifier)
  const baseline = [{ fpr: 0, tpr: 0 }, { fpr: 1, tpr: 1 }];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-secondary)', margin: 0 }}>
          ROC Curve
        </h3>
        <div style={{
          padding: '8px 16px',
          background: 'rgba(0,245,255,0.08)',
          border: '1px solid rgba(0,245,255,0.2)',
          borderRadius: 20,
          fontSize: 14,
          color: 'var(--cyan)',
          fontFamily: 'JetBrains Mono, monospace',
          fontWeight: 700,
        }}>
          AUC-ROC: 0.9847
        </div>
      </div>

      <ResponsiveContainer width="100%" height={340}>
        <LineChart margin={{ top: 4, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="fpr"
            domain={[0, 1]}
            tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
            axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
            tickLine={false}
            label={{ value: 'False Positive Rate', position: 'insideBottom', offset: -4, fill: 'rgba(255,255,255,0.3)', fontSize: 12 }}
          />
          <YAxis
            type="number"
            dataKey="tpr"
            domain={[0, 1]}
            tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            label={{ value: 'True Positive Rate', angle: -90, position: 'insideLeft', fill: 'rgba(255,255,255,0.3)', fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Baseline */}
          <Line
            data={baseline}
            type="linear"
            dataKey="tpr"
            stroke="rgba(255,255,255,0.15)"
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={false}
            name="Random"
          />

          {/* ROC Curve */}
          <Line
            data={data}
            type="monotone"
            dataKey="tpr"
            stroke="#00F5FF"
            strokeWidth={2.5}
            dot={{ fill: '#00F5FF', r: 3, strokeWidth: 0 }}
            activeDot={{ r: 5, fill: '#fff', stroke: '#00F5FF', strokeWidth: 2 }}
            name="XGBoost"
          />
        </LineChart>
      </ResponsiveContainer>

      <div style={{ display: 'flex', gap: 20, marginTop: 12, fontSize: 12, color: 'rgba(255,255,255,0.4)', justifyContent: 'center' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 20, height: 2, background: '#00F5FF', display: 'inline-block', borderRadius: 1 }} />
          XGBoost (AUC=0.9847)
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 20, height: 2, background: 'rgba(255,255,255,0.2)', display: 'inline-block', borderRadius: 1, borderTop: '1px dashed rgba(255,255,255,0.3)' }} />
          Random Classifier
        </span>
      </div>
    </div>
  );
}
