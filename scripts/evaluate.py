"""Evaluate PPO + all 4 baselines on 2024 test split.

Outputs:
  results/comparison_2024.csv
  results/equity_curves.png

Pattern from FinRL FinRL_StockTrading_2026_3_Backtest.py:196-206
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from baselines.buy_and_hold import BuyAndHold
from baselines.mean_reversion import MeanReversion
from baselines.momentum import Momentum
from baselines.random_agent import RandomAgent
from baselines.metrics import compute_all
from env.crypto_trading_env import CryptoTradingEnv, OHLCV_COLS
from env import SEED

BASELINES = {
    "buy_hold": BuyAndHold(),
    "mean_rev": MeanReversion(),
    "momentum": Momentum(),
    "random": RandomAgent(),
}


def load_split(asset: str, split: str) -> pd.DataFrame:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", f"{asset}_features.csv")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    result = df[df["split"] == split].copy()
    return result.reset_index().rename(columns={"index": "date"})


def compute_train_stats(df_train: pd.DataFrame) -> dict:
    means = df_train[OHLCV_COLS].mean().to_dict()
    stds = {k: max(v, 1e-8) for k, v in df_train[OHLCV_COLS].std().to_dict().items()}
    return {"means": means, "stds": stds}


def run_ppo(asset: str, df_test: pd.DataFrame, train_stats: dict, initial_balance: float):
    """Load trained model and run on test split."""
    from agents.ppo_agent import PPOAgent

    model_path = os.path.join(os.path.dirname(__file__), "..", "models", f"ppo_{asset}_final.zip")
    if not os.path.exists(model_path):
        print(f"  PPO model not found at {model_path}, skipping PPO")
        return None, None

    agent = PPOAgent.load(model_path)
    env = CryptoTradingEnv(df_test.copy(), scaler_stats=train_stats)
    obs, _ = env.reset(seed=SEED)

    portfolio_values = [initial_balance]
    done = False
    while not done:
        action = agent.predict(obs)
        obs, reward, terminated, truncated, info = env.step(int(action))
        portfolio_values.append(info["net_worth"])
        done = terminated or truncated

    dates = df_test["date"].values[:len(portfolio_values)]
    equity = pd.Series(portfolio_values[:len(dates)], index=dates, name="ppo")
    trade_log = env.trades
    return trade_log, equity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset", required=True, choices=["btc", "eth", "sol"])
    parser.add_argument("--balance", type=float, default=10_000.0)
    args = parser.parse_args()

    df_train = load_split(args.asset, "train")
    df_test = load_split(args.asset, "test")
    train_stats = compute_train_stats(df_train)

    print(f"Evaluating {args.asset} on test split ({len(df_test)} rows)...")

    all_metrics = []
    all_equity = {}

    # PPO
    trade_log, equity = run_ppo(args.asset, df_test, train_stats, args.balance)
    if equity is not None:
        metrics = compute_all(equity, trade_log)
        metrics["strategy"] = "ppo"
        all_metrics.append(metrics)
        all_equity["ppo"] = equity

    # Baselines
    for name, strategy in BASELINES.items():
        trade_log, equity = strategy.run(df_test.copy(), initial_balance=args.balance)
        metrics = compute_all(equity, trade_log)
        metrics["strategy"] = name
        all_metrics.append(metrics)
        all_equity[name] = equity

    # Print summary
    df_metrics = pd.DataFrame(all_metrics).set_index("strategy")
    print("\n--- Results ---")
    print(df_metrics.to_string())

    # Save CSV
    results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(results_dir, exist_ok=True)
    df_metrics.to_csv(os.path.join(results_dir, "comparison_2024.csv"))
    print(f"\nSaved results/comparison_2024.csv")

    # Plot equity curves
    fig, ax = plt.subplots(figsize=(12, 6))
    for name, equity in all_equity.items():
        ax.plot(equity.index, equity.values, label=name)
    ax.set_title(f"{args.asset.upper()} — Equity Curves (2024 Test Split)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(results_dir, "equity_curves.png"), dpi=150)
    print("Saved results/equity_curves.png")


if __name__ == "__main__":
    main()
