import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { TrainingCurves as TCData } from "../api";

interface Props { data: TCData; }

export default function TrainingCurves({ data }: Props) {
  if (!data.episodes.length) {
    return (
      <div style={{
        padding: 24, border: "1px solid var(--border)", borderRadius: "var(--radius-md)",
        background: "var(--bg-surface)", color: "var(--text-muted)", fontSize: 12, textAlign: "center",
      }}>
        Training curves not available — export TensorBoard data from Colab first.
      </div>
    );
  }

  const chartData = data.episodes.map((ep, i) => ({ episode: ep, reward: data.rewards[i] }));

  return (
    <div>
      <div className="label" style={{ marginBottom: 12 }}>Training Curves — {data.asset.toUpperCase()}</div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="episode" tick={{ fill: "var(--text-muted)", fontSize: 10 }} />
          <YAxis tick={{ fill: "var(--text-muted)", fontSize: 10 }} />
          <Tooltip
            contentStyle={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", borderRadius: 6, fontSize: 12 }}
            formatter={(v) => [Number(v).toFixed(3), "Reward"]}
          />
          <Line type="monotone" dataKey="reward" stroke="#d29922" dot={false} strokeWidth={2} name="Episode Reward" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
