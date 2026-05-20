import type { CompareRow } from "../api";

interface Props { rows: CompareRow[]; }

function pct(v: number) { return `${v >= 0 ? "+" : ""}${(v * 100).toFixed(1)}%`; }
function num(v: number) { return v.toFixed(3); }

export default function ComparisonTable({ rows }: Props) {
  const sorted = [...rows].sort((a, b) => b.sharpe - a.sharpe);
  const maxSharpe = Math.max(...sorted.map(r => r.sharpe));

  return (
    <div style={{ overflowX: "auto" }}>
      <table className="data-table">
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>#</th>
            <th style={{ textAlign: "left" }}>Strategy</th>
            <th>Sharpe</th>
            <th>Return</th>
            <th>Max DD</th>
            <th>Win Rate</th>
            <th>Calmar</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, i) => {
            const isBest = row.sharpe === maxSharpe && row.sharpe > 0;
            const sharpeBar = maxSharpe > 0 ? (row.sharpe / maxSharpe) * 80 : 0;
            return (
              <tr key={row.strategy}>
                <td style={{ color: i === 0 ? "var(--yellow)" : "var(--text-muted)", fontWeight: i === 0 ? 700 : 400 }}>
                  {i + 1}
                </td>
                <td>
                  <span style={{
                    color: isBest ? "var(--accent)" : "var(--text-primary)",
                    fontWeight: isBest ? 700 : 400,
                  }}>
                    {row.strategy}
                  </span>
                  {isBest && <span style={{ marginLeft: 8, fontSize: 10, color: "var(--yellow)" }}>★ best</span>}
                </td>
                <td style={{ textAlign: "right" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 8 }}>
                    <div style={{
                      height: 4, width: Math.max(sharpeBar, 0),
                      background: row.sharpe > 0 ? "var(--green)" : "var(--red)",
                      borderRadius: 2, opacity: 0.7,
                    }} />
                    <span style={{ color: row.sharpe > 0 ? "var(--green)" : "var(--red)", minWidth: 44, textAlign: "right" }}>
                      {num(row.sharpe)}
                    </span>
                  </div>
                </td>
                <td style={{ textAlign: "right", color: row.total_return > 0 ? "var(--green)" : "var(--red)" }}>
                  {pct(row.total_return)}
                </td>
                <td style={{ textAlign: "right", color: "var(--red)" }}>
                  {pct(row.max_drawdown)}
                </td>
                <td style={{ textAlign: "right", color: "var(--text-secondary)" }}>
                  {pct(row.win_rate)}
                </td>
                <td style={{ textAlign: "right", color: row.calmar > 0 ? "var(--green)" : "var(--red)" }}>
                  {num(row.calmar)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
