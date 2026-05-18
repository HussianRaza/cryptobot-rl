"""Random baseline: random action each step.

Must use explicit seed for reproducibility — the RL-eth-agent reference
(models.py:18-62) doesn't seed, making it non-reproducible. Fixed here.
"""
import pandas as pd
import numpy as np
from baselines.base import BaselineStrategy

SEED = 42


class RandomAgent(BaselineStrategy):
    def __init__(self, seed: int = SEED):
        self.seed = seed

    def run(self, df: pd.DataFrame, initial_balance: float = 10_000.0):
        rng = np.random.default_rng(self.seed)
        df = df.reset_index(drop=True)
        close = df["close"].values
        dates = df["date"].values if "date" in df.columns else df.index.values

        balance = initial_balance
        units = 0.0
        trade_log = []
        equity = []

        for i, price in enumerate(close):
            # Actions: 0=buy25, 1=buy50, 2=hold, 3=sell25, 4=sell50
            action = int(rng.integers(0, 5))

            if action in (0, 1) and balance > 1:
                fraction = 0.25 if action == 0 else 0.50
                spend = balance * fraction
                new_units = spend / price
                units += new_units
                balance -= spend
                trade_log.append({
                    "Date": dates[i], "Close": price,
                    "total": spend, "type": "buy",
                    "Net_worth": balance + units * price, "profits": 0.0,
                })
            elif action in (3, 4) and units > 1e-8:
                fraction = 0.25 if action == 3 else 0.50
                sell_units = units * fraction
                proceeds = sell_units * price
                profit = proceeds - sell_units * (
                    sum(t["total"] for t in trade_log if t["type"] == "buy") /
                    max(sum(t["total"] / t["Close"] for t in trade_log if t["type"] == "buy"), 1e-8)
                )
                units -= sell_units
                balance += proceeds
                trade_log.append({
                    "Date": dates[i], "Close": price,
                    "total": proceeds, "type": "sell",
                    "Net_worth": balance + units * price, "profits": profit,
                })

            equity.append(balance + units * price)

        return trade_log, pd.Series(equity, index=dates, name="random")
