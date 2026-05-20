import { useState } from "react";
import type { TradeEntry } from "../api";

const PAGE_SIZE = 20;

interface Props { trades: TradeEntry[]; }

export default function TradeLog({ trades }: Props) {
  const [page, setPage] = useState(0);
  const total = Math.ceil(trades.length / PAGE_SIZE);
  const slice = trades.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  if (!trades.length) return <p style={{ color: "#888" }}>No trades recorded.</p>;

  return (
    <div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "#2a2a4a", color: "#e0e0e0" }}>
              {["Date", "Type", "Close ($)", "Total ($)", "Net Worth ($)", "Profit ($)"].map(h => (
                <th key={h} style={{ padding: "6px 10px", borderBottom: "1px solid #444", textAlign: "right",
                                     ...(h === "Date" || h === "Type" ? { textAlign: "left" } : {}) }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {slice.map((t, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? "#1a1a2e" : "#22223b" }}>
                <td style={{ padding: "6px 10px" }}>{String(t.Date).slice(0, 10)}</td>
                <td style={{ padding: "6px 10px", color: t.type === "buy" ? "#7cfc00" : "#ff6b6b" }}>{t.type}</td>
                <td style={{ padding: "6px 10px", textAlign: "right" }}>{t.Close?.toFixed(2)}</td>
                <td style={{ padding: "6px 10px", textAlign: "right" }}>{t.total?.toFixed(2)}</td>
                <td style={{ padding: "6px 10px", textAlign: "right" }}>{t.Net_worth?.toFixed(2)}</td>
                <td style={{ padding: "6px 10px", textAlign: "right", color: (t.profits ?? 0) >= 0 ? "#7cfc00" : "#ff6b6b" }}>
                  {(t.profits ?? 0).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {total > 1 && (
        <div style={{ marginTop: 8, display: "flex", gap: 8, alignItems: "center" }}>
          <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}>Prev</button>
          <span style={{ color: "#aaa" }}>Page {page + 1} / {total}</span>
          <button onClick={() => setPage(p => Math.min(total - 1, p + 1))} disabled={page === total - 1}>Next</button>
        </div>
      )}
    </div>
  );
}
