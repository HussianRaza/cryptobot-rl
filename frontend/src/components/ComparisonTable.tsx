import React from "react";
import type { CompareRow } from "../api";

interface Props { rows: CompareRow[]; }

function pct(v: number) { return `${(v * 100).toFixed(2)}%`; }
function num(v: number) { return v.toFixed(3); }

export default function ComparisonTable({ rows }: Props) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
        <thead>
          <tr style={{ background: "#2a2a4a", color: "#e0e0e0" }}>
            {["Strategy", "Sharpe", "Max DD", "Total Return", "Win Rate", "Calmar"].map(h => (
              <th key={h} style={{ padding: "8px 12px", textAlign: "right", borderBottom: "1px solid #444" }}
                  {...(h === "Strategy" ? { style: { padding: "8px 12px", textAlign: "left", borderBottom: "1px solid #444" } } : {})}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={row.strategy} style={{ background: i % 2 === 0 ? "#1a1a2e" : "#22223b" }}>
              <td style={{ padding: "8px 12px", color: "#a0c4ff" }}>{row.strategy}</td>
              <td style={{ padding: "8px 12px", textAlign: "right", color: row.sharpe >= 0 ? "#7cfc00" : "#ff6b6b" }}>{num(row.sharpe)}</td>
              <td style={{ padding: "8px 12px", textAlign: "right" }}>{pct(row.max_drawdown)}</td>
              <td style={{ padding: "8px 12px", textAlign: "right", color: row.total_return >= 0 ? "#7cfc00" : "#ff6b6b" }}>{pct(row.total_return)}</td>
              <td style={{ padding: "8px 12px", textAlign: "right" }}>{pct(row.win_rate)}</td>
              <td style={{ padding: "8px 12px", textAlign: "right", color: row.calmar >= 0 ? "#7cfc00" : "#ff6b6b" }}>{num(row.calmar)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
