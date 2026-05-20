import { useEffect, useState } from "react";

interface FGData { value: string; value_classification: string; }

function getColor(v: number) {
  if (v <= 25) return "var(--red)";
  if (v <= 45) return "#e3790a";
  if (v <= 55) return "var(--yellow)";
  if (v <= 75) return "#6bca76";
  return "var(--green)";
}

export default function FearGreed() {
  const [data, setData] = useState<FGData | null>(null);

  useEffect(() => {
    fetch("https://api.alternative.me/fng/?limit=1")
      .then(r => r.json()).then(d => setData(d.data[0])).catch(() => {});
  }, []);

  if (!data) return null;

  const value = parseInt(data.value);
  const color = getColor(value);
  const R = 26, cx = 32, cy = 32;
  const startAngle = 210 * (Math.PI / 180);
  const endAngle   = (210 + 300 * (value / 100)) * (Math.PI / 180);
  const trackEnd   = (210 + 300) * (Math.PI / 180);

  const arc = (a1: number, a2: number) => {
    const x1 = cx + R * Math.cos(a1), y1 = cy + R * Math.sin(a1);
    const x2 = cx + R * Math.cos(a2), y2 = cy + R * Math.sin(a2);
    return `M ${x1} ${y1} A ${R} ${R} 0 ${a2 - a1 > Math.PI ? 1 : 0} 1 ${x2} ${y2}`;
  };

  return (
    <div style={{ padding: "10px 12px", borderTop: "1px solid var(--border)" }}>
      <div className="label" style={{ marginBottom: 8 }}>Market Sentiment</div>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <svg width={64} height={48} style={{ overflow: "visible" }}>
          <path d={arc(startAngle, trackEnd)} fill="none" stroke="var(--bg-elevated)" strokeWidth={5} strokeLinecap="round" />
          {value > 0 && <path d={arc(startAngle, endAngle)} fill="none" stroke={color} strokeWidth={5} strokeLinecap="round" />}
          <text x={cx} y={cy + 6} textAnchor="middle" fontSize={12} fontWeight="700" fill={color}
            fontFamily="var(--font-mono)">{value}</text>
        </svg>
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color }}>{data.value_classification}</div>
          <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 2 }}>Fear & Greed</div>
        </div>
      </div>
    </div>
  );
}
