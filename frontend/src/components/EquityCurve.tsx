import { useMemo } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";
import type { EquityPoint } from "../api";

interface Props { data: EquityPoint[]; title: string; }

export default function EquityCurve({ data, title }: Props) {
  const chartData = useMemo(() =>
    data.map(d => ({ date: d.date.slice(0, 10), value: Math.round(d.value) })),
    [data]
  );

  if (!data.length) return <p style={{ color: "var(--text-muted)", fontSize: 12 }}>No data.</p>;

  const start = 10_000;
  const end = chartData.at(-1)?.value ?? start;
  const lineColor = end >= start ? "var(--green)" : "var(--red)";
  const gradientId = `equity-grad-${title.replace(/\s/g, "")}`;

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>{title}</span>
        <span style={{
          fontSize: 13, fontWeight: 700,
          color: end >= start ? "var(--green)" : "var(--red)",
        }}>
          {end >= start ? "▲" : "▼"} ${end.toLocaleString()}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor={end >= start ? "#3fb950" : "#f85149"} stopOpacity={0.2} />
              <stop offset="95%" stopColor={end >= start ? "#3fb950" : "#f85149"} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="date" tick={{ fill: "var(--text-muted)", fontSize: 10 }} tickFormatter={v => v.slice(5)} />
          <YAxis tick={{ fill: "var(--text-muted)", fontSize: 10 }} tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} />
          <ReferenceLine y={start} stroke="var(--border-bright)" strokeDasharray="4 4" label={{ value: "Start", fill: "var(--text-muted)", fontSize: 10 }} />
          <Tooltip
            contentStyle={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", borderRadius: 6, fontSize: 12 }}
            labelStyle={{ color: "var(--text-secondary)" }}
            formatter={(v) => [`$${Number(v).toLocaleString()}`, "Portfolio"]}
          />
          <Area type="monotone" dataKey="value" stroke={lineColor} strokeWidth={2}
            fill={`url(#${gradientId})`} dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
