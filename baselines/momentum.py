"""Momentum baseline: buy on 5-day positive streak, sell on 3-day negative streak."""
import pandas as pd
import numpy as np
from baselines.base import BaselineStrategy


class Momentum(BaselineStrategy):
    def __init__(self, buy_streak: int = 5, sell_streak: int = 3):
        self.buy_streak = buy_streak
        self.sell_streak = sell_streak

    def run(self, df: pd.DataFrame, initial_balance: float = 10_000.0):
        df = df.reset_index(drop=True)
        close = df["close"].values
        dates = df["date"].values if "date" in df.columns else df.index.values

        balance = initial_balance
        units = 0.0
        trade_log = []
        equity = []

        pos_streak = 0
        neg_streak = 0

        for i in range(len(close)):
            price = close[i]
            if i > 0:
                if close[i] > close[i - 1]:
                    pos_streak += 1
                    neg_streak = 0
                elif close[i] < close[i - 1]:
                    neg_streak += 1
                    pos_streak = 0
                else:
                    pos_streak = 0
                    neg_streak = 0

            if units == 0.0 and pos_streak >= self.buy_streak and balance > 1:
                units = balance / price
                balance = 0.0
                trade_log.append({
                    "Date": dates[i], "Close": price,
                    "total": units * price, "type": "buy",
                    "Net_worth": units * price, "profits": 0.0,
                })
            elif units > 0.0 and neg_streak >= self.sell_streak:
                proceeds = units * price
                buy_cost = sum(t["total"] for t in trade_log[-1:] if t["type"] == "buy")
                trade_log.append({
                    "Date": dates[i], "Close": price,
                    "total": proceeds, "type": "sell",
                    "Net_worth": proceeds, "profits": proceeds - buy_cost,
                })
                balance = proceeds
                units = 0.0

            equity.append(balance + units * price)

        return trade_log, pd.Series(equity, index=dates, name="momentum")
