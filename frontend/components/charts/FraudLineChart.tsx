'use client';

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart,
} from 'recharts';

interface DataPoint {
  day: string;
  fraudRate: number;
  transactions: number;
  flagged: number;
}

interface FraudLineChartProps {
  data: DataPoint[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(5,8,19,0.95)',
      border: '1px solid rgba(0,245,255,0.2)',
      borderRadius: 10,
      padding: '12px 16px',
      fontSize: 13,
    }}>
      <div style={{ color: '#fff', fontWeight: 600, marginBottom: 8 }}>{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} style={{ color: p.color, display: 'flex', justifyContent: 'space-between', gap: 24 }}>
          <span>{p.name}</span>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 600 }}>{p.value}</span>
        </div>
      ))}
    </div>
  );
};

export default function FraudLineChart({ data }: FraudLineChartProps) {
  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-secondary)', margin: '0 0 20px' }}>
        Fraud Rate Trend (30 Days)
      </h3>
      <ResponsiveContainer width="100%" height={340}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="fraudGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#FF2D55" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#FF2D55" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="flaggedGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00F5FF" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#00F5FF" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
          <XAxis
            dataKey="day"
            tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
            axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
            tickLine={false}
            interval={4}
          />
          <YAxis
            tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', paddingTop: 12 }}
          />
          <Area
            type="monotone"
            dataKey="fraudRate"
            name="Fraud Rate (%)"
            stroke="#FF2D55"
            strokeWidth={2}
            fill="url(#fraudGrad)"
            dot={false}
          />
          <Area
            type="monotone"
            dataKey="flagged"
            name="Flagged Txns"
            stroke="#00F5FF"
            strokeWidth={2}
            fill="url(#flaggedGrad)"
            dot={false}
            yAxisId="right"
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
