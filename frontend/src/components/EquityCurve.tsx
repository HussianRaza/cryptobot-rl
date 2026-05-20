import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { EquityPoint } from "../api";

interface Props {
  data: EquityPoint[];
  title: string;
}

export default function EquityCurve({ data, title }: Props) {
  if (!data.length) return <p style={{ color: "#888" }}>No data available.</p>;

  const chartData = data.map(d => ({ date: d.date.slice(0, 10), value: Math.round(d.value) }));

  return (
    <div>
      <p style={{ color: "#ccc", marginBottom: 8 }}>{title}</p>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="date" tick={{ fill: "#aaa", fontSize: 11 }} tickFormatter={v => v.slice(0, 7)} />
          <YAxis tick={{ fill: "#aaa", fontSize: 11 }} tickFormatter={v => `$${v.toLocaleString()}`} />
          <Tooltip
            contentStyle={{ background: "#1a1a2e", border: "1px solid #444", color: "#eee" }}
            formatter={(v: number) => [`$${v.toLocaleString()}`, "Portfolio"]}
          />
          <Line type="monotone" dataKey="value" stroke="#4f8ef7" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
