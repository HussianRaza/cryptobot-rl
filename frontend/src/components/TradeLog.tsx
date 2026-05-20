import { useState } from "react";
import type { TradeEntry } from "../api";

const PAGE_SIZE = 20;
interface Props { trades: TradeEntry[]; }

export default function TradeLog({ trades }: Props) {
  const [page, setPage] = useState(0);
  const total = Math.ceil(trades.length / PAGE_SIZE);
  const slice = trades.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  if (!trades.length) return <p style={{ color: "var(--text-muted)", fontSize: 12 }}>No trades recorded.</p>;

  return (
    <div>
      <div style={{ overflowX: "auto", borderRadius: "var(--radius-md)", border: "1px solid var(--border)" }}>
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ textAlign: "left" }}>Date</th>
              <th style={{ textAlign: "left" }}>Type</th>
              <th style={{ textAlign: "right" }}>Price</th>
              <th style={{ textAlign: "right" }}>Total</th>
              <th style={{ textAlign: "right" }}>Net Worth</th>
              <th style={{ textAlign: "right" }}>P&L</th>
            </tr>
          </thead>
          <tbody>
            {slice.map((t, i) => {
              const isBuy = t.type === "buy";
              const profit = t.profits ?? 0;
              return (
                <tr key={i} style={{ borderLeft: `3px solid ${isBuy ? "var(--green)" : "var(--red)"}` }}>
                  <td style={{ color: "var(--text-secondary)" }}>{String(t.Date).slice(0, 10)}</td>
                  <td>
                    <span className={isBuy ? "badge badge-green" : "badge badge-red"} style={{ fontSize: 11 }}>
                      {isBuy ? "▲ BUY" : "▼ SELL"}
                    </span>
                  </td>
                  <td style={{ textAlign: "right" }}>${Number(t.Close).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td style={{ textAlign: "right" }}>${Number(t.total).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td style={{ textAlign: "right" }}>${Number(t.Net_worth).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td style={{ textAlign: "right", color: profit >= 0 ? "var(--green)" : "var(--red)" }}>
                    {profit >= 0 ? "+" : ""}{profit.toFixed(0)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {total > 1 && (
        <div style={{ marginTop: 12, display: "flex", gap: 8, alignItems: "center" }}>
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            style={{
              padding: "5px 12px", borderRadius: "var(--radius-sm)",
              background: "var(--bg-elevated)", border: "1px solid var(--border)",
              color: page === 0 ? "var(--text-muted)" : "var(--text-primary)",
              fontSize: 12, cursor: page === 0 ? "default" : "pointer",
            }}
          >← Prev</button>
          <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
            {page + 1} / {total}
          </span>
          <button
            onClick={() => setPage(p => Math.min(total - 1, p + 1))}
            disabled={page === total - 1}
            style={{
              padding: "5px 12px", borderRadius: "var(--radius-sm)",
              background: "var(--bg-elevated)", border: "1px solid var(--border)",
              color: page === total - 1 ? "var(--text-muted)" : "var(--text-primary)",
              fontSize: 12, cursor: page === total - 1 ? "default" : "pointer",
            }}
          >Next →</button>
        </div>
      )}
    </div>
  );
}
