import React, { useEffect, useState } from "react";

interface FGData {
  value: string;
  value_classification: string;
  timestamp: string;
}

function getColor(v: number): string {
  if (v <= 25) return "#ef5350";
  if (v <= 45) return "#ff8c00";
  if (v <= 55) return "#ffd700";
  if (v <= 75) return "#66bb6a";
  return "#4caf50";
}

export default function FearGreed() {
  const [data, setData] = useState<FGData | null>(null);

  useEffect(() => {
    fetch("https://api.alternative.me/fng/?limit=1")
      .then(r => r.json())
      .then(d => setData(d.data[0]))
      .catch(() => {});
  }, []);

  if (!data) return null;

  const value = parseInt(data.value);
  const color = getColor(value);
  const pct = value / 100;

  // Arc from 210° to 330° (bottom-weighted semicircle), filled by value
  const R = 28;
  const cx = 36, cy = 36;
  const startAngle = 210 * (Math.PI / 180);
  const endAngle = (210 + 300 * pct) * (Math.PI / 180);
  const arcPath = (a1: number, a2: number) => {
    const x1 = cx + R * Math.cos(a1), y1 = cy + R * Math.sin(a1);
    const x2 = cx + R * Math.cos(a2), y2 = cy + R * Math.sin(a2);
    const large = a2 - a1 > Math.PI ? 1 : 0;
    return `M ${x1} ${y1} A ${R} ${R} 0 ${large} 1 ${x2} ${y2}`;
  };
  const trackEnd = (210 + 300) * (Math.PI / 180);

  return (
    <div style={{
      background: "#1a1a2e", borderRadius: 10, padding: "8px 14px",
      display: "flex", alignItems: "center", gap: 10, border: "1px solid #2a2a3e",
    }}>
      <svg width={72} height={52} style={{ overflow: "visible" }}>
        <path d={arcPath(startAngle, trackEnd)} fill="none" stroke="#2a2a3e" strokeWidth={6} strokeLinecap="round" />
        {pct > 0 && (
          <path d={arcPath(startAngle, endAngle)} fill="none" stroke={color} strokeWidth={6} strokeLinecap="round" />
        )}
        <text x={cx} y={cy + 4} textAnchor="middle" fontSize={13} fontWeight="bold" fill={color}>{value}</text>
      </svg>
      <div>
        <div style={{ fontSize: 10, color: "#666", marginBottom: 2 }}>Fear & Greed</div>
        <div style={{ fontSize: 13, fontWeight: 600, color }}>{data.value_classification}</div>
      </div>
    </div>
  );
}
