import React from "react";

const ASSETS = ["btc", "eth", "sol"];
const AGENTS = ["ppo", "buy_hold", "mean_rev", "momentum", "random"];

interface Props {
  asset: string;
  agent: string;
  onAssetChange: (a: string) => void;
  onAgentChange: (a: string) => void;
}

export default function AssetAgentSelector({ asset, agent, onAssetChange, onAgentChange }: Props) {
  return (
    <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
      <label>
        Asset:{" "}
        <select value={asset} onChange={e => onAssetChange(e.target.value)}>
          {ASSETS.map(a => <option key={a} value={a}>{a.toUpperCase()}</option>)}
        </select>
      </label>
      <label>
        Strategy:{" "}
        <select value={agent} onChange={e => onAgentChange(e.target.value)}>
          {AGENTS.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
      </label>
    </div>
  );
}
