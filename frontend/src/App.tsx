import { useEffect, useState } from "react";
import EquityCurve from "./components/EquityCurve";
import ComparisonTable from "./components/ComparisonTable";
import TrainingCurves from "./components/TrainingCurves";
import TradeLog from "./components/TradeLog";
import DisclaimerPage from "./components/DisclaimerPage";
import PriceTicker from "./components/PriceTicker";
import FearGreed from "./components/FearGreed";
import PaperTrading from "./components/PaperTrading";
import { fetchBacktest, fetchCompare, fetchTrainingCurves } from "./api";
import type { BacktestResult, CompareResult, TrainingCurves as TCData } from "./api";

type Tab = "backtest" | "compare" | "paper" | "training" | "disclaimer";

const ASSETS = ["btc", "eth", "sol"] as const;
const AGENTS = ["ppo", "buy_hold", "mean_rev", "momentum", "random"] as const;
const TABS: { key: Tab; label: string }[] = [
  { key: "backtest",   label: "Backtest" },
  { key: "compare",    label: "Compare" },
  { key: "paper",      label: "Live Paper" },
  { key: "training",   label: "Training" },
  { key: "disclaimer", label: "Disclaimer" },
];

const ASSET_COLORS: Record<string, string> = {
  btc: "#f7931a", eth: "#627eea", sol: "#9945ff",
};

export default function App() {
  const [asset, setAsset] = useState<string>("btc");
  const [agent, setAgent] = useState<string>("ppo");
  const [tab, setTab]     = useState<Tab>("backtest");
  const [backtest, setBacktest] = useState<BacktestResult | null>(null);
  const [compare,  setCompare]  = useState<CompareResult | null>(null);
  const [curves,   setCurves]   = useState<TCData | null>(null);
  const [loading, setLoading]   = useState(false);
  const [error,   setError]     = useState("");

  useEffect(() => {
    if (tab === "backtest") load(fetchBacktest(asset, agent), setBacktest);
    if (tab === "compare")  load(fetchCompare(asset), setCompare);
    if (tab === "training") load(fetchTrainingCurves(asset), setCurves);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [asset, agent, tab]);

  async function load<T>(promise: Promise<T>, setter: (v: T) => void) {
    setLoading(true); setError("");
    try { setter(await promise); }
    catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  }

  const metrics = backtest?.metrics;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: "var(--bg-base)", color: "var(--text-primary)", overflow: "hidden" }}>

      {/* ── Header ── */}
      <header style={{
        height: 48, minHeight: 48,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 20px",
        borderBottom: "1px solid var(--border)",
        background: "var(--bg-surface)",
        gap: 16, flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 16, color: "var(--accent)", fontWeight: 700, letterSpacing: "-0.5px" }}>◈ CryptoRL</span>
          <span style={{ color: "var(--text-muted)", fontSize: 11 }}>PPO vs Baselines · 2024</span>
        </div>
        <PriceTicker />
      </header>

      {/* ── Body: sidebar + main ── */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>

        {/* ── Sidebar ── */}
        <aside style={{
          width: 200, minWidth: 200, flexShrink: 0,
          background: "var(--bg-surface)",
          borderRight: "1px solid var(--border)",
          display: "flex", flexDirection: "column",
          padding: "16px 0",
          overflowY: "auto",
        }}>

          {/* Asset selector */}
          <div style={{ padding: "0 14px", marginBottom: 6 }}>
            <span className="label">Asset</span>
          </div>
          {ASSETS.map(a => (
            <button
              key={a}
              onClick={() => setAsset(a)}
              style={{
                display: "flex", alignItems: "center", gap: 10,
                padding: "8px 14px",
                background: asset === a ? "var(--bg-elevated)" : "none",
                borderLeft: `3px solid ${asset === a ? ASSET_COLORS[a] : "transparent"}`,
                color: asset === a ? "var(--text-primary)" : "var(--text-secondary)",
                fontSize: 13, fontWeight: asset === a ? 600 : 400,
                textAlign: "left", width: "100%",
                transition: "all 0.15s",
              }}
            >
              <span style={{
                width: 8, height: 8, borderRadius: "50%",
                background: asset === a ? ASSET_COLORS[a] : "var(--border-bright)",
                flexShrink: 0,
              }} />
              {a.toUpperCase()}
            </button>
          ))}

          {/* Strategy selector */}
          <div style={{ padding: "16px 14px 6px" }}>
            <span className="label">Strategy</span>
          </div>
          {AGENTS.map(ag => (
            <button
              key={ag}
              onClick={() => setAgent(ag)}
              style={{
                display: "flex", alignItems: "center", gap: 8,
                padding: "7px 14px",
                background: agent === ag ? "var(--bg-elevated)" : "none",
                borderLeft: `3px solid ${agent === ag ? "var(--accent)" : "transparent"}`,
                color: agent === ag ? "var(--text-primary)" : "var(--text-secondary)",
                fontSize: 12, fontWeight: agent === ag ? 600 : 400,
                textAlign: "left", width: "100%",
                transition: "all 0.15s",
              }}
            >
              <span style={{ color: agent === ag ? "var(--accent)" : "transparent", fontSize: 10 }}>▸</span>
              {ag}
            </button>
          ))}

          {/* Fear & Greed at bottom */}
          <div style={{ marginTop: "auto", padding: "16px 14px 0" }}>
            <FearGreed />
          </div>
        </aside>

        {/* ── Main content ── */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>

          {/* Tab bar */}
          <nav style={{
            display: "flex", alignItems: "center", gap: 2,
            padding: "0 20px",
            borderBottom: "1px solid var(--border)",
            background: "var(--bg-surface)",
            flexShrink: 0, height: 42,
          }}>
            {TABS.map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                style={{
                  padding: "0 14px", height: "100%",
                  fontSize: 12, fontWeight: tab === key ? 600 : 400,
                  color: tab === key ? "var(--text-primary)" : "var(--text-secondary)",
                  borderBottom: `2px solid ${tab === key ? "var(--accent)" : "transparent"}`,
                  borderTop: "2px solid transparent",
                  transition: "all 0.15s",
                }}
              >
                {key === "paper" && <span style={{ marginRight: 5, fontSize: 8, color: "var(--green)" }}>●</span>}
                {label}
              </button>
            ))}
          </nav>

          {/* Content */}
          <main style={{ flex: 1, overflowY: "auto", padding: 20 }}>
            {loading && (
              <div style={{ color: "var(--text-muted)", fontSize: 12, padding: "20px 0" }}>Loading...</div>
            )}
            {error && (
              <div style={{
                background: "rgba(248,81,73,0.08)", border: "1px solid rgba(248,81,73,0.3)",
                borderRadius: "var(--radius-sm)", padding: "10px 14px",
                color: "var(--red)", fontSize: 12, marginBottom: 16,
              }}>
                {error}
              </div>
            )}

            {/* ── Backtest ── */}
            {tab === "backtest" && backtest && metrics && (
              <div>
                {/* Metrics row */}
                <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
                  {([
                    { label: "Sharpe",       val: metrics.sharpe.toFixed(3),                  color: metrics.sharpe > 0 ? "var(--green)" : "var(--red)" },
                    { label: "Total Return", val: (metrics.total_return * 100).toFixed(1) + "%", color: metrics.total_return > 0 ? "var(--green)" : "var(--red)" },
                    { label: "Max Drawdown", val: (metrics.max_drawdown * 100).toFixed(1) + "%", color: "var(--red)" },
                    { label: "Win Rate",     val: (metrics.win_rate * 100).toFixed(1) + "%",     color: "var(--text-primary)" },
                    { label: "Calmar",       val: metrics.calmar.toFixed(3),                   color: metrics.calmar > 0 ? "var(--green)" : "var(--red)" },
                  ]).map(({ label, val, color }) => (
                    <div key={label} className="card" style={{ minWidth: 120 }}>
                      <div className="label" style={{ marginBottom: 8 }}>{label}</div>
                      <div className="num" style={{ color }}>{val}</div>
                    </div>
                  ))}
                </div>

                <EquityCurve data={backtest.equity_curve} title={`${asset.toUpperCase()} · ${agent}`} />

                <div style={{ marginTop: 24 }}>
                  <div className="label" style={{ marginBottom: 12 }}>Trade Log</div>
                  <TradeLog trades={backtest.trade_log} />
                </div>
              </div>
            )}

            {/* ── Compare ── */}
            {tab === "compare" && compare && (
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                  <span style={{
                    width: 10, height: 10, borderRadius: "50%",
                    background: ASSET_COLORS[asset], display: "inline-block",
                  }} />
                  <span style={{ color: "var(--text-secondary)", fontSize: 12 }}>
                    {asset.toUpperCase()} · All strategies · 2024 test period
                  </span>
                </div>
                <ComparisonTable rows={compare.rows} />
              </div>
            )}

            {/* ── Paper Trading ── */}
            {tab === "paper" && <PaperTrading asset={asset} />}

            {/* ── Training ── */}
            {tab === "training" && curves && <TrainingCurves data={curves} />}

            {/* ── Disclaimer ── */}
            {tab === "disclaimer" && <DisclaimerPage />}
          </main>
        </div>
      </div>
    </div>
  );
}
