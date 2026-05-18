import React from "react";
import Plot from "react-plotly.js";
import type { TrainingCurves as TCData } from "../api";

interface Props { data: TCData; }

export default function TrainingCurves({ data }: Props) {
  if (!data.episodes.length) {
    return <p style={{ color: "#888" }}>Training curves not available — train model on Colab first.</p>;
  }
  return (
    <Plot
      data={[{
        x: data.episodes,
        y: data.rewards,
        type: "scatter",
        mode: "lines",
        name: "Episode Reward",
        line: { color: "#f7a44f" },
      }]}
      layout={{
        title: `Training Curves — ${data.asset.toUpperCase()}`,
        xaxis: { title: "Episode" },
        yaxis: { title: "Mean Reward" },
        margin: { t: 40, r: 20, b: 40, l: 60 },
        plot_bgcolor: "#1a1a2e",
        paper_bgcolor: "#1a1a2e",
        font: { color: "#e0e0e0" },
      }}
      style={{ width: "100%", height: 300 }}
      config={{ responsive: true }}
    />
  );
}
