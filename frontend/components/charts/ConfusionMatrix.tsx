'use client';

interface CMData {
  tp: number;
  fp: number;
  fn: number;
  tn: number;
}

interface ConfusionMatrixProps {
  data: CMData;
}

export default function ConfusionMatrix({ data }: ConfusionMatrixProps) {
  const { tp, fp, fn, tn } = data;
  const total = tp + fp + fn + tn;

  const cells = [
    { label: 'True Positive', abbr: 'TP', value: tp, color: '#10B981', bg: 'rgba(16,185,129,0.12)', predicted: 'Fraud', actual: 'Fraud' },
    { label: 'False Positive', abbr: 'FP', value: fp, color: '#F59E0B', bg: 'rgba(245,158,11,0.12)', predicted: 'Fraud', actual: 'Legit' },
    { label: 'False Negative', abbr: 'FN', value: fn, color: '#EF4444', bg: 'rgba(239,68,68,0.12)', predicted: 'Legit', actual: 'Fraud' },
    { label: 'True Negative', abbr: 'TN', value: tn, color: '#10B981', bg: 'rgba(16,185,129,0.08)', predicted: 'Legit', actual: 'Legit' },
  ];

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-secondary)', margin: '0 0 20px' }}>
        Confusion Matrix
      </h3>

      <div style={{ display: 'flex', gap: 40, alignItems: 'flex-start', flexWrap: 'wrap' }}>
        {/* Matrix Grid */}
        <div>
          {/* Axis Labels */}
          <div style={{ display: 'flex', marginBottom: 8 }}>
            <div style={{ width: 100 }} />
            <div style={{ flex: 1, textAlign: 'center', fontSize: 12, color: 'rgba(255,255,255,0.4)', fontWeight: 600 }}>
              Predicted Fraud
            </div>
            <div style={{ flex: 1, textAlign: 'center', fontSize: 12, color: 'rgba(255,255,255,0.4)', fontWeight: 600 }}>
              Predicted Legit
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {['Fraud', 'Legit'].map((actualLabel, row) => (
              <div key={actualLabel} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <div style={{
                  width: 100,
                  fontSize: 12,
                  color: 'rgba(255,255,255,0.4)',
                  fontWeight: 600,
                  textAlign: 'right',
                  paddingRight: 12,
                  flexShrink: 0,
                }}>
                  Actual {actualLabel}
                </div>
                {['Fraud', 'Legit'].map((predLabel) => {
                  const cell = cells.find(
                    (c) => c.actual === actualLabel && c.predicted === predLabel,
                  )!;
                  const pct = ((cell.value / total) * 100).toFixed(2);
                  return (
                    <div
                      key={predLabel}
                      style={{
                        width: 140,
                        height: 120,
                        background: cell.bg,
                        border: `2px solid ${cell.color}40`,
                        borderRadius: 12,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: 4,
                        transition: 'all 0.2s',
                        cursor: 'default',
                      }}
                    >
                      <div style={{ fontSize: 11, color: cell.color, fontWeight: 700, letterSpacing: '0.08em' }}>
                        {cell.abbr}
                      </div>
                      <div style={{
                        fontSize: 28,
                        fontWeight: 800,
                        color: cell.color,
                        fontFamily: 'JetBrains Mono, monospace',
                        lineHeight: 1,
                      }}>
                        {cell.value.toLocaleString()}
                      </div>
                      <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>{pct}%</div>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>

          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginTop: 8, paddingLeft: 100 }}>
            Total samples: {total.toLocaleString()}
          </div>
        </div>

        {/* Derived Metrics */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, minWidth: 200 }}>
          {[
            { label: 'Sensitivity (Recall)', value: tp / (tp + fn), color: '#10B981' },
            { label: 'Specificity', value: tn / (tn + fp), color: 'var(--cyan)' },
            { label: 'Precision (PPV)', value: tp / (tp + fp), color: 'var(--purple)' },
            { label: 'False Positive Rate', value: fp / (fp + tn), color: '#F59E0B' },
            { label: 'False Negative Rate', value: fn / (fn + tp), color: '#EF4444' },
          ].map((m) => (
            <div key={m.label} style={{
              padding: '12px 16px',
              background: 'rgba(255,255,255,0.03)',
              borderRadius: 10,
              border: '1px solid rgba(255,255,255,0.06)',
            }}>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginBottom: 4 }}>{m.label}</div>
              <div style={{
                fontSize: 20,
                fontWeight: 700,
                color: m.color,
                fontFamily: 'JetBrains Mono, monospace',
              }}>
                {(m.value * 100).toFixed(2)}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
