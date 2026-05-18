const BASE = "http://localhost:8000";

export interface Metrics {
  sharpe: number;
  max_drawdown: number;
  total_return: number;
  win_rate: number;
  calmar: number;
}

export interface EquityPoint { date: string; value: number; }

export interface TradeEntry {
  Date: string;
  Close: number;
  total: number;
  type: "buy" | "sell";
  Net_worth: number;
  profits: number;
}

export interface BacktestResult {
  metrics: Metrics;
  trade_log: TradeEntry[];
  equity_curve: EquityPoint[];
}

export interface CompareRow {
  strategy: string;
  sharpe: number;
  max_drawdown: number;
  total_return: number;
  win_rate: number;
  calmar: number;
}

export interface CompareResult { asset: string; rows: CompareRow[]; }
export interface TrainingCurves { asset: string; episodes: number[]; rewards: number[]; }
export interface PortfolioHistory { asset: string; agent: string; dates: string[]; values: number[]; }

async function apiFetch<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const fetchBacktest = (asset: string, agent: string) =>
  apiFetch<BacktestResult>(`${BASE}/api/backtest?asset=${asset}&agent=${agent}`);

export const fetchCompare = (asset: string) =>
  apiFetch<CompareResult>(`${BASE}/api/compare?asset=${asset}`);

export const fetchTrainingCurves = (asset: string) =>
  apiFetch<TrainingCurves>(`${BASE}/api/training-curves?asset=${asset}`);

export const fetchPortfolioHistory = (asset: string, agent: string) =>
  apiFetch<PortfolioHistory>(`${BASE}/api/portfolio-history?asset=${asset}&agent=${agent}`);

export const fetchDisclaimer = () =>
  apiFetch<{ text: string }>(`${BASE}/api/disclaimer`);
