import { useEffect, useState } from "react";

interface PriceData {
  bitcoin:  { usd: number; usd_24h_change: number };
  ethereum: { usd: number; usd_24h_change: number };
  solana:   { usd: number; usd_24h_change: number };
}

const COINS = [
  { id: "bitcoin",  label: "BTC", color: "#f7931a" },
  { id: "ethereum", label: "ETH", color: "#627eea" },
  { id: "solana",   label: "SOL", color: "#9945ff" },
] as const;

export default function PriceTicker() {
  const [prices, setPrices] = useState<PriceData | null>(null);

  async function fetchPrices() {
    try {
      const res = await fetch(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
      );
      if (res.ok) setPrices(await res.json());
    } catch {}
  }

  useEffect(() => {
    fetchPrices();
    const id = setInterval(fetchPrices, 30_000);
    return () => clearInterval(id);
  }, []);

  if (!prices) return null;

  return (
    <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
      {COINS.map(({ id, label, color }) => {
        const d = prices[id];
        const up = d.usd_24h_change >= 0;
        return (
          <div key={id} style={{ display: "flex", alignItems: "baseline", gap: 5 }}>
            <span style={{ fontSize: 10, fontWeight: 700, color, letterSpacing: "0.05em" }}>{label}</span>
            <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
              ${d.usd.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </span>
            <span style={{ fontSize: 11, color: up ? "var(--green)" : "var(--red)" }}>
              {up ? "▲" : "▼"}{Math.abs(d.usd_24h_change).toFixed(1)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}
