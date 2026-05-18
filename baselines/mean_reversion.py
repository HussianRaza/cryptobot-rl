"""Mean-reversion baseline: buy when price < 20-day MA * 0.98, sell above 20-day MA."""
import pandas as pd
import numpy as np
from baselines.base import BaselineStrategy


class MeanReversion(BaselineStrategy):
    def __init__(self, window: int = 20, buy_threshold: float = 0.98):
        self.window = window
        self.buy_threshold = buy_threshold

    def run(self, df: pd.DataFrame, initial_balance: float = 10_000.0):
        df = df.reset_index(drop=True)
        close = df["close"].values
        dates = df["date"].values if "date" in df.columns else df.index.values
        ma = pd.Series(close).rolling(self.window, min_periods=1).mean().values

        balance = initial_balance
        units = 0.0
        trade_log = []
        equity = []

        for i, (price, ma_val) in enumerate(zip(close, ma)):
            if units == 0.0 and price < ma_val * self.buy_threshold and balance > 1:
                units = balance / price
                balance = 0.0
                trade_log.append({
                    "Date": dates[i], "Close": price,
                    "total": units * price, "type": "buy",
                    "Net_worth": units * price, "profits": 0.0,
                })
            elif units > 0.0 and price > ma_val:
                proceeds = units * price
                profit = proceeds - sum(t["total"] for t in trade_log if t["type"] == "buy")
                trade_log.append({
                    "Date": dates[i], "Close": price,
                    "total": proceeds, "type": "sell",
                    "Net_worth": proceeds, "profits": profit,
                })
                balance = proceeds
                units = 0.0

            equity.append(balance + units * price)

        return trade_log, pd.Series(equity, index=dates, name="mean_reversion")
