import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";
import { fetchPaperTrading } from "../api";
import type { PaperTradingResult, TradeEntry } from "../api";

const PAPER_AGENTS = ["buy_hold", "mean_rev", "momentum", "random"] as const;
const DAYS_OPTIONS = [30, 60, 90, 180] as const;

interface Props { asset: string; }

export default function PaperTrading({ asset }: Props) {
  const [agent, setAgent] = useState<string>("buy_hold");
  const [days, setDays] = useState<number>(60);
  const [data, setData] = useState<PaperTradingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  async function load() {
    setLoading(true); setError("");
    try {
      setData(await fetchPaperTrading(asset, agent, days));
      setLastRefresh(new Date());
    } catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, [asset, agent, days]);

  const signal = data?.current_signal;
  const signalColor = signal === "long" ? "#4caf50" : "#aaa";
  const signalLabel = signal === "long" ? "▲ LONG" : "— FLAT";
  const pnlColor = data && data.pnl_pct >= 0 ? "#4caf50" : "#ef5350";

  const chartData = data?.equity_curve.map(p => ({
    date: p.date.slice(0, 10),
    value: Math.round(p.value),
  })) ?? [];

  return (
    <div>
      {/* Controls */}
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap", alignItems: "center" }}>
        <div>
          <label style={{ color: "#888", fontSize: 12, display: "block", marginBottom: 4 }}>Strategy</label>
          <select
            value={agent}
            onChange={e => setAgent(e.target.value)}
            style={{ background: "#1a1a2e", color: "#e0e0e0", border: "1px solid #333", borderRadius: 6, padding: "6px 10px" }}
          >
            {PAPER_AGENTS.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
        <div>
          <label style={{ color: "#888", fontSize: 12, display: "block", marginBottom: 4 }}>Window</label>
          <select
            value={days}
            onChange={e => setDays(Number(e.target.value))}
            style={{ background: "#1a1a2e", color: "#e0e0e0", border: "1px solid #333", borderRadius: 6, padding: "6px 10px" }}
          >
            {DAYS_OPTIONS.map(d => <option key={d} value={d}>Last {d} days</option>)}
          </select>
        </div>
        <button
          onClick={load}
          disabled={loading}
          style={{ marginTop: 18, padding: "6px 16px", background: "#1a3a5c", color: "#a0c4ff", border: "1px solid #2a4a7c", borderRadius: 6, cursor: "pointer" }}
        >
          {loading ? "Refreshing…" : "↻ Refresh"}
        </button>
        {lastRefresh && (
          <span style={{ marginTop: 18, fontSize: 11, color: "#444" }}>
            Live data · updated {lastRefresh.toLocaleTimeString()}
          </span>
        )}
      </div>

      {error && <p style={{ color: "#ef5350" }}>Error: {error}</p>}

      {data && (
        <>
          {/* Stats row */}
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
            <StatCard label="Current Value" value={`$${data.current_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} color="#a0c4ff" />
            <StatCard label={`P&L (${days}d)`} value={`${data.pnl_pct >= 0 ? "+" : ""}${(data.pnl_pct * 100).toFixed(1)}%`} color={pnlColor} />
            <StatCard label="Sharpe" value={data.metrics.sharpe.toFixed(2)} color="#a0c4ff" />
            <StatCard label="Max DD" value={`${(data.metrics.max_drawdown * 100).toFixed(1)}%`} color="#ef5350" />
            <div style={{ background: "#1a1a2e", padding: "12px 18px", borderRadius: 8, border: "1px solid #2a2a3e", minWidth: 110 }}>
              <div style={{ color: "#888", fontSize: 12, marginBottom: 4 }}>Signal Today</div>
              <div style={{ fontSize: 20, fontWeight: "bold", color: signalColor }}>{signalLabel}</div>
            </div>
          </div>

          {/* Equity chart */}
          <div style={{ marginBottom: 24 }}>
            <p style={{ color: "#888", fontSize: 12, margin: "0 0 8px" }}>
              {asset.toUpperCase()} · {agent} · ${data.initial_balance.toLocaleString()} starting capital · live data from CoinGecko
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis dataKey="date" tick={{ fill: "#666", fontSize: 11 }} tickFormatter={v => v.slice(5)} />
                <YAxis tick={{ fill: "#666", fontSize: 11 }} tickFormatter={v => `$${v.toLocaleString()}`} />
                <ReferenceLine y={data.initial_balance} stroke="#444" strokeDasharray="4 4" label={{ value: "Start", fill: "#555", fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ background: "#1a1a2e", border: "1px solid #333", color: "#eee" }}
                  formatter={(v) => [`$${Number(v).toLocaleString()}`, "Portfolio"]}
                />
                <Line type="monotone" dataKey="value" stroke="#4f8ef7" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Trade log */}
          {data.trade_log.length > 0 && (
            <>
              <h4 style={{ color: "#a0c4ff", margin: "0 0 10px" }}>Trades</h4>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ background: "#1a1a2e" }}>
                    {["Date", "Type", "Price", "Portfolio"].map(h => (
                      <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "#888", fontWeight: 500 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[...data.trade_log].reverse().map((t: TradeEntry, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #1a1a2e" }}>
                      <td style={{ padding: "7px 12px", color: "#aaa" }}>{String(t.Date).slice(0, 10)}</td>
                      <td style={{ padding: "7px 12px", color: t.type === "buy" ? "#4caf50" : "#ef5350", fontWeight: 600 }}>
                        {t.type.toUpperCase()}
                      </td>
                      <td style={{ padding: "7px 12px" }}>${Number(t.Close).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                      <td style={{ padding: "7px 12px" }}>${Number(t.Net_worth).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{ background: "#1a1a2e", padding: "12px 18px", borderRadius: 8, border: "1px solid #2a2a3e", minWidth: 110 }}>
      <div style={{ color: "#888", fontSize: 12, marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: "bold", color }}>{value}</div>
    </div>
  );
}
