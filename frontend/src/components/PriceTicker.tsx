import { useEffect, useState } from "react";

interface PriceData {
  bitcoin: { usd: number; usd_24h_change: number };
  ethereum: { usd: number; usd_24h_change: number };
  solana: { usd: number; usd_24h_change: number };
}

const COINS = [
  { id: "bitcoin", label: "BTC" },
  { id: "ethereum", label: "ETH" },
  { id: "solana", label: "SOL" },
] as const;

export default function PriceTicker() {
  const [prices, setPrices] = useState<PriceData | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  async function fetchPrices() {
    try {
      const res = await fetch(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
      );
      if (res.ok) {
        setPrices(await res.json());
        setLastUpdate(new Date());
      }
    } catch {}
  }

  useEffect(() => {
    fetchPrices();
    const id = setInterval(fetchPrices, 30_000);
    return () => clearInterval(id);
  }, []);

  if (!prices) return <span style={{ color: "#555", fontSize: 12 }}>Loading prices...</span>;

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
      {COINS.map(({ id, label }) => {
        const d = prices[id];
        const up = d.usd_24h_change >= 0;
        return (
          <div key={id} style={{ display: "flex", alignItems: "baseline", gap: 5 }}>
            <span style={{ color: "#666", fontSize: 11, fontWeight: 600 }}>{label}</span>
            <span style={{ fontSize: 15, fontWeight: "bold", color: "#e0e0e0" }}>
              ${d.usd.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </span>
            <span style={{ fontSize: 12, color: up ? "#4caf50" : "#ef5350" }}>
              {up ? "▲" : "▼"}{Math.abs(d.usd_24h_change).toFixed(2)}%
            </span>
          </div>
        );
      })}
      {lastUpdate && (
        <span style={{ fontSize: 10, color: "#444" }}>
          {lastUpdate.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
}
