import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { TrainingCurves as TCData } from "../api";

interface Props { data: TCData; }

export default function TrainingCurves({ data }: Props) {
  if (!data.episodes.length) {
    return <p style={{ color: "#888" }}>Training curves not available — train model on Colab first.</p>;
  }

  const chartData = data.episodes.map((ep, i) => ({ episode: ep, reward: data.rewards[i] }));

  return (
    <div>
      <p style={{ color: "#ccc", marginBottom: 8 }}>Training Curves — {data.asset.toUpperCase()}</p>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="episode" tick={{ fill: "#aaa", fontSize: 11 }} />
          <YAxis tick={{ fill: "#aaa", fontSize: 11 }} />
          <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #444", color: "#eee" }} />
          <Line type="monotone" dataKey="reward" stroke="#f7a44f" dot={false} strokeWidth={2} name="Episode Reward" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
