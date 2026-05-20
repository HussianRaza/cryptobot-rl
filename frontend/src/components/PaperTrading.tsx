import { useEffect, useState } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";
import { fetchPaperTrading } from "../api";
import type { PaperTradingResult, TradeEntry } from "../api";

const PAPER_AGENTS   = ["ppo", "buy_hold", "mean_rev", "momentum", "random"] as const;
const DAYS_OPTIONS   = [30, 60, 90, 180] as const;

interface Props { asset: string; }

export default function PaperTrading({ asset }: Props) {
  const [agent, setAgent] = useState("buy_hold");
  const [days,  setDays]  = useState(60);
  const [data,  setData]  = useState<PaperTradingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  async function load() {
    setLoading(true); setError("");
    try { setData(await fetchPaperTrading(asset, agent, days)); setLastRefresh(new Date()); }
    catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, [asset, agent, days]);

  const isLong   = data?.current_signal === "long";
  const pnlUp    = (data?.pnl_pct ?? 0) >= 0;
  const gradId   = "paper-grad";

  const chartData = data?.equity_curve.map(p => ({
    date: p.date.slice(0, 10), value: Math.round(p.value),
  })) ?? [];

  return (
    <div>
      {/* Controls */}
      <div style={{ display: "flex", gap: 12, marginBottom: 20, alignItems: "flex-end", flexWrap: "wrap" }}>
        <div>
          <div className="label" style={{ marginBottom: 6 }}>Strategy</div>
          <select
            value={agent} onChange={e => setAgent(e.target.value)}
            style={{
              background: "var(--bg-elevated)", color: "var(--text-primary)",
              border: "1px solid var(--border)", borderRadius: "var(--radius-sm)",
              padding: "6px 10px", fontSize: 12,
            }}
          >
            {PAPER_AGENTS.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
        <div>
          <div className="label" style={{ marginBottom: 6 }}>Window</div>
          <select
            value={days} onChange={e => setDays(Number(e.target.value))}
            style={{
              background: "var(--bg-elevated)", color: "var(--text-primary)",
              border: "1px solid var(--border)", borderRadius: "var(--radius-sm)",
              padding: "6px 10px", fontSize: 12,
            }}
          >
            {DAYS_OPTIONS.map(d => <option key={d} value={d}>Last {d} days</option>)}
          </select>
        </div>
        <button
          onClick={load} disabled={loading}
          style={{
            padding: "6px 16px", borderRadius: "var(--radius-sm)",
            background: "var(--bg-elevated)", border: "1px solid var(--border-bright)",
            color: "var(--accent)", fontSize: 12,
          }}
        >
          {loading ? "..." : "↻ Refresh"}
        </button>
        {lastRefresh && (
          <span style={{ fontSize: 10, color: "var(--text-muted)" }}>
            live · {lastRefresh.toLocaleTimeString()}
          </span>
        )}
      </div>

      {error && (
        <div style={{
          background: "rgba(248,81,73,0.08)", border: "1px solid rgba(248,81,73,0.3)",
          borderRadius: "var(--radius-sm)", padding: "10px 14px",
          color: "var(--red)", fontSize: 12, marginBottom: 16,
        }}>{error}</div>
      )}

      {data && (
        <>
          {/* Stats */}
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
            <div className="card" style={{ minWidth: 130 }}>
              <div className="label" style={{ marginBottom: 8 }}>Portfolio Value</div>
              <div className="num" style={{ color: "var(--text-primary)" }}>
                ${data.current_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </div>
            </div>
            <div className="card" style={{ minWidth: 110 }}>
              <div className="label" style={{ marginBottom: 8 }}>P&L ({days}d)</div>
              <div className="num" style={{ color: pnlUp ? "var(--green)" : "var(--red)" }}>
                {pnlUp ? "+" : ""}{(data.pnl_pct * 100).toFixed(1)}%
              </div>
            </div>
            <div className="card" style={{ minWidth: 100 }}>
              <div className="label" style={{ marginBottom: 8 }}>Sharpe</div>
              <div className="num" style={{ color: data.metrics.sharpe > 0 ? "var(--green)" : "var(--red)" }}>
                {data.metrics.sharpe.toFixed(2)}
              </div>
            </div>
            <div className="card" style={{ minWidth: 100 }}>
              <div className="label" style={{ marginBottom: 8 }}>Max DD</div>
              <div className="num" style={{ color: "var(--red)" }}>
                {(data.metrics.max_drawdown * 100).toFixed(1)}%
              </div>
            </div>
            {/* Signal badge */}
            <div className="card" style={{ minWidth: 120 }}>
              <div className="label" style={{ marginBottom: 8 }}>Signal Today</div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span
                  className="pulse"
                  style={{
                    width: 8, height: 8, borderRadius: "50%", flexShrink: 0,
                    background: isLong ? "var(--green)" : "var(--text-muted)",
                  }}
                />
                <span style={{
                  fontSize: 15, fontWeight: 700,
                  color: isLong ? "var(--green)" : "var(--text-secondary)",
                }}>
                  {isLong ? "LONG" : "FLAT"}
                </span>
              </div>
            </div>
          </div>

          {/* Chart */}
          <div style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8 }}>
              {asset.toUpperCase()} · {agent} · $10,000 starting capital · Yahoo Finance
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
                <defs>
                  <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor={pnlUp ? "#3fb950" : "#f85149"} stopOpacity={0.2} />
                    <stop offset="95%" stopColor={pnlUp ? "#3fb950" : "#f85149"} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="date" tick={{ fill: "var(--text-muted)", fontSize: 10 }} tickFormatter={v => v.slice(5)} />
                <YAxis tick={{ fill: "var(--text-muted)", fontSize: 10 }} tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} />
                <ReferenceLine y={data.initial_balance} stroke="var(--border-bright)" strokeDasharray="4 4"
                  label={{ value: "Start", fill: "var(--text-muted)", fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", borderRadius: 6, fontSize: 12 }}
                  formatter={(v) => [`$${Number(v).toLocaleString()}`, "Portfolio"]}
                />
                <Area type="monotone" dataKey="value"
                  stroke={pnlUp ? "var(--green)" : "var(--red)"} strokeWidth={2}
                  fill={`url(#${gradId})`} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Trade log */}
          {data.trade_log.length > 0 && (
            <>
              <div className="label" style={{ marginBottom: 10 }}>Trades</div>
              <div style={{ borderRadius: "var(--radius-md)", border: "1px solid var(--border)", overflow: "hidden" }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th style={{ textAlign: "left" }}>Date</th>
                      <th style={{ textAlign: "left" }}>Type</th>
                      <th style={{ textAlign: "right" }}>Price</th>
                      <th style={{ textAlign: "right" }}>Portfolio</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...data.trade_log].reverse().map((t: TradeEntry, i) => {
                      const isBuy = t.type === "buy";
                      return (
                        <tr key={i} style={{ borderLeft: `3px solid ${isBuy ? "var(--green)" : "var(--red)"}` }}>
                          <td style={{ color: "var(--text-secondary)" }}>{String(t.Date).slice(0, 10)}</td>
                          <td>
                            <span className={isBuy ? "badge badge-green" : "badge badge-red"} style={{ fontSize: 11 }}>
                              {isBuy ? "▲ BUY" : "▼ SELL"}
                            </span>
                          </td>
                          <td style={{ textAlign: "right" }}>${Number(t.Close).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                          <td style={{ textAlign: "right" }}>${Number(t.Net_worth).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
