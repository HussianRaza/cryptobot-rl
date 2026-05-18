import React from "react";
import Plot from "react-plotly.js";
import type { EquityPoint } from "../api";

interface Props {
  data: EquityPoint[];
  title: string;
}

export default function EquityCurve({ data, title }: Props) {
  return (
    <Plot
      data={[{
        x: data.map(d => d.date),
        y: data.map(d => d.value),
        type: "scatter",
        mode: "lines",
        name: "Portfolio Value",
        line: { color: "#4f8ef7" },
      }]}
      layout={{
        title,
        xaxis: { title: "Date" },
        yaxis: { title: "Portfolio Value ($)" },
        margin: { t: 40, r: 20, b: 40, l: 60 },
        plot_bgcolor: "#1a1a2e",
        paper_bgcolor: "#1a1a2e",
        font: { color: "#e0e0e0" },
      }}
      style={{ width: "100%", height: 350 }}
      config={{ responsive: true }}
    />
  );
}
