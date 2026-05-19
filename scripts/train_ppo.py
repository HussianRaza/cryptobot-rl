"""Train PPO agent on a single asset.

Usage:
  python scripts/train_ppo.py --asset btc --timesteps 500000 --seed 42 --tag final

Runs on local CPU or Google Colab T4. Saves model to models/ppo_{asset}_{tag}.zip
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import torch
import pandas as pd
import numpy as np

from env.crypto_trading_env import CryptoTradingEnv, OHLCV_COLS
from agents.ppo_agent import PPOAgent, DEVICE
from env import SEED

SPLIT_DATES = {
    "train": ("2020-01-01", "2022-12-31"),
    "val":   ("2023-01-01", "2023-12-31"),
    "test":  ("2024-01-01", "2024-12-31"),
}


def load_split_df(asset: str, split: str) -> pd.DataFrame:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", f"{asset}_features.csv")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    result = df[df["split"] == split].copy()
    result = result.reset_index()
    result = result.rename(columns={"index": "date"})
    return result


def compute_train_stats(df_train: pd.DataFrame) -> dict:
    """Fit OHLCV z-score stats on train split only."""
    means = df_train[OHLCV_COLS].mean().to_dict()
    stds = {k: max(v, 1e-8) for k, v in df_train[OHLCV_COLS].std().to_dict().items()}
    return {"means": means, "stds": stds}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset", required=True, choices=["btc", "eth", "sol"])
    parser.add_argument("--timesteps", type=int, default=500_000)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--tag", default="final")
    parser.add_argument("--n-envs", type=int, default=4)
    parser.add_argument("--n-steps", type=int, default=None, help="PPO rollout steps per env (overrides default)")
    parser.add_argument("--batch-size", type=int, default=None, help="PPO minibatch size (overrides default)")
    parser.add_argument("--subproc", action="store_true", help="Use SubprocVecEnv for true parallel envs")
    parser.add_argument("--checkpoint-freq", type=int, default=10_000)
    args = parser.parse_args()

    print(f"Training PPO on {args.asset} for {args.timesteps:,} timesteps (seed={args.seed}, tag={args.tag})")
    print(f"  device: {DEVICE}" + (f" ({torch.cuda.get_device_name(0)})" if DEVICE == "cuda" else ""))

    df_train = load_split_df(args.asset, "train")
    print(f"  train rows: {len(df_train)}")

    train_stats = compute_train_stats(df_train)

    def env_factory():
        return CryptoTradingEnv(df_train.copy(), scaler_stats=train_stats)

    agent = PPOAgent()
    agent.build(
        env_factory,
        n_envs=args.n_envs,
        n_steps=args.n_steps,
        batch_size=args.batch_size,
        use_subproc=args.subproc,
    )

    checkpoint_dir = os.path.join(os.path.dirname(__file__), "..", "models", "checkpoints", args.asset)
    agent.train(timesteps=args.timesteps, checkpoint_dir=checkpoint_dir)

    model_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    os.makedirs(model_dir, exist_ok=True)
    save_path = os.path.join(model_dir, f"ppo_{args.asset}_{args.tag}")
    agent.save(save_path)
    print(f"Model saved to {save_path}.zip")

    # Quick validation step on val split
    df_val = load_split_df(args.asset, "val")
    val_env = CryptoTradingEnv(df_val, scaler_stats=train_stats)
    obs, _ = val_env.reset(seed=args.seed)
    episode_reward = 0.0
    done = False
    while not done:
        action = agent.predict(obs)
        obs, reward, terminated, truncated, info = val_env.step(int(action))
        episode_reward += reward
        done = terminated or truncated
    print(f"  val episode reward: {episode_reward:.4f}  final net worth: {info['net_worth']:.2f}")


if __name__ == "__main__":
    main()
