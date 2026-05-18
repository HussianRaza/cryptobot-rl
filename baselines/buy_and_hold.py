"""Buy-and-hold baseline: buy all-in day 1, hold to end.

Pattern adapted from RLTrader benchmarks.py buy_and_hodl.
"""
import pandas as pd
from baselines.base import BaselineStrategy


class BuyAndHold(BaselineStrategy):
    def run(self, df: pd.DataFrame, initial_balance: float = 10_000.0):
        df = df.reset_index(drop=True)
        entry_price = float(df["close"].iloc[0])
        units = initial_balance / entry_price

        equity = pd.Series(
            units * df["close"].values,
            index=df["date"] if "date" in df.columns else df.index,
            name="buy_and_hold",
        )

        buy_entry = {
            "Date": df["date"].iloc[0] if "date" in df.columns else df.index[0],
            "Close": entry_price,
            "total": initial_balance,
            "type": "buy",
            "Net_worth": initial_balance,
            "profits": 0.0,
        }
        exit_price = float(df["close"].iloc[-1])
        sell_exit = {
            "Date": df["date"].iloc[-1] if "date" in df.columns else df.index[-1],
            "Close": exit_price,
            "total": units * exit_price,
            "type": "sell",
            "Net_worth": units * exit_price,
            "profits": units * exit_price - initial_balance,
        }
        return [buy_entry, sell_exit], equity
