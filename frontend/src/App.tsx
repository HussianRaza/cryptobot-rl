import React, { useEffect, useState } from "react";
import AssetAgentSelector from "./components/AssetAgentSelector";
import EquityCurve from "./components/EquityCurve";
import ComparisonTable from "./components/ComparisonTable";
import TrainingCurves from "./components/TrainingCurves";
import TradeLog from "./components/TradeLog";
import DisclaimerPage from "./components/DisclaimerPage";
import PriceTicker from "./components/PriceTicker";
import FearGreed from "./components/FearGreed";
import {
  fetchBacktest, fetchCompare, fetchTrainingCurves,
} from "./api";
import type { BacktestResult, CompareResult, TrainingCurves as TCData } from "./api";

type Tab = "backtest" | "compare" | "training" | "disclaimer";

const tabStyle = (active: boolean): React.CSSProperties => ({
  padding: "8px 18px",
  cursor: "pointer",
  borderBottom: active ? "2px solid #4f8ef7" : "2px solid transparent",
  color: active ? "#4f8ef7" : "#aaa",
  background: "none",
  border: "none",
  fontSize: 15,
});

export default function App() {
  const [asset, setAsset] = useState("btc");
  const [agent, setAgent] = useState("ppo");
  const [tab, setTab] = useState<Tab>("backtest");
  const [backtest, setBacktest] = useState<BacktestResult | null>(null);
  const [compare, setCompare] = useState<CompareResult | null>(null);
  const [curves, setCurves] = useState<TCData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (tab === "backtest") loadBacktest();
    if (tab === "compare") loadCompare();
    if (tab === "training") loadCurves();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [asset, agent, tab]);

  async function loadBacktest() {
    setLoading(true); setError("");
    try { setBacktest(await fetchBacktest(asset, agent)); }
    catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  }

  async function loadCompare() {
    setLoading(true); setError("");
    try { setCompare(await fetchCompare(asset)); }
    catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  }

  async function loadCurves() {
    setLoading(true); setError("");
    try { setCurves(await fetchTrainingCurves(asset)); }
    catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  }

  return (
    <div style={{ background: "#0f0f1a", minHeight: "100vh", color: "#e0e0e0", fontFamily: "sans-serif" }}>
      <header style={{ padding: "14px 24px", borderBottom: "1px solid #222", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 20, color: "#a0c4ff" }}>Crypto RL Trading Bot</h1>
          <p style={{ margin: "3px 0 0", color: "#666", fontSize: 12 }}>
            PPO vs Classical Strategies · 2024 Test Period
          </p>
        </div>
        <PriceTicker />
      </header>

      <div style={{ padding: "14px 24px", display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
        <AssetAgentSelector asset={asset} agent={agent} onAssetChange={setAsset} onAgentChange={setAgent} />
        <FearGreed />
      </div>

      <nav style={{ display: "flex", padding: "0 24px", borderBottom: "1px solid #333" }}>
        {(["backtest", "compare", "training", "disclaimer"] as Tab[]).map(t => (
          <button key={t} style={tabStyle(tab === t)} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </nav>

      <main style={{ padding: "24px" }}>
        {loading && <p style={{ color: "#4f8ef7" }}>Loading...</p>}
        {error && <p style={{ color: "#ff6b6b" }}>Error: {error}</p>}

        {tab === "backtest" && backtest && (
          <div>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 20 }}>
              {[
                ["Sharpe", backtest.metrics.sharpe.toFixed(3)],
                ["Max DD", (backtest.metrics.max_drawdown * 100).toFixed(2) + "%"],
                ["Total Return", (backtest.metrics.total_return * 100).toFixed(2) + "%"],
                ["Win Rate", (backtest.metrics.win_rate * 100).toFixed(1) + "%"],
                ["Calmar", backtest.metrics.calmar.toFixed(3)],
              ].map(([label, val]) => (
                <div key={label} style={{ background: "#1a1a2e", padding: "12px 18px", borderRadius: 8, minWidth: 110 }}>
                  <div style={{ color: "#888", fontSize: 12 }}>{label}</div>
                  <div style={{ fontSize: 20, fontWeight: "bold", color: "#a0c4ff" }}>{val}</div>
                </div>
              ))}
            </div>
            <EquityCurve data={backtest.equity_curve} title={`${asset.toUpperCase()} — ${agent} Equity Curve`} />
            <h3 style={{ marginTop: 24, color: "#a0c4ff" }}>Trade Log</h3>
            <TradeLog trades={backtest.trade_log} />
          </div>
        )}

        {tab === "compare" && compare && (
          <div>
            <h3 style={{ color: "#a0c4ff" }}>{asset.toUpperCase()} — All Strategies (2024 Test Period)</h3>
            <ComparisonTable rows={compare.rows} />
          </div>
        )}

        {tab === "training" && curves && <TrainingCurves data={curves} />}

        {tab === "disclaimer" && <DisclaimerPage />}
      </main>
    </div>
  );
}
