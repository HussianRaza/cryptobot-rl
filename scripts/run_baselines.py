"""Run all 4 baseline strategies on a given asset/year split."""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from baselines.buy_and_hold import BuyAndHold
from baselines.mean_reversion import MeanReversion
from baselines.momentum import Momentum
from baselines.random_agent import RandomAgent
from baselines.metrics import compute_all

STRATEGIES = {
    "buy_hold": BuyAndHold(),
    "mean_rev": MeanReversion(),
    "momentum": Momentum(),
    "random": RandomAgent(),
}


def load_test_df(asset: str) -> pd.DataFrame:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", f"{asset}_features.csv")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    result = df[df["split"] == "test"].copy()
    return result.reset_index().rename(columns={"index": "date"})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset", required=True, choices=["btc", "eth", "sol"])
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--balance", type=float, default=10_000.0)
    args = parser.parse_args()

    df = load_test_df(args.asset)
    print(f"Running baselines on {args.asset} test split ({len(df)} rows, balance=${args.balance:,.0f})\n")

    rows = []
    for name, strategy in STRATEGIES.items():
        trade_log, equity = strategy.run(df.copy(), initial_balance=args.balance)
        metrics = compute_all(equity, trade_log)
        metrics["strategy"] = name
        rows.append(metrics)
        print(f"{name:12s}  sharpe={metrics['sharpe']:+.3f}  return={metrics['total_return']:+.2%}  "
              f"mdd={metrics['max_drawdown']:.2%}  wr={metrics['win_rate']:.2%}  calmar={metrics['calmar']:+.3f}")

    return rows


if __name__ == "__main__":
    main()
