"""Run check_env and 100 random steps to validate CryptoTradingEnv."""
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from env.crypto_trading_env import CryptoTradingEnv
from stable_baselines3.common.env_checker import check_env


def load_split(asset: str, split: str) -> pd.DataFrame:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", f"{asset}_features.csv")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df[df["split"] == split].reset_index().rename(columns={"index": "date"})


def main():
    asset = sys.argv[1] if len(sys.argv) > 1 else "btc"
    print(f"Smoke-testing env on {asset} train split...")

    df_train = load_split(asset, "train")
    print(f"  train rows: {len(df_train)}")

    env = CryptoTradingEnv(df_train)

    print("  running check_env()...")
    check_env(env, warn=True)
    print("  check_env() passed")

    print("  running 100 random steps...")
    obs, info = env.reset(seed=42)
    assert obs.shape == env.observation_space.shape, f"obs shape mismatch: {obs.shape}"

    rewards = []
    for i in range(100):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        rewards.append(reward)
        assert np.isfinite(reward), f"non-finite reward at step {i}: {reward}"
        assert obs.shape == env.observation_space.shape
        if terminated or truncated:
            obs, info = env.reset()

    print(f"  mean reward: {np.mean(rewards):.4f}  min: {np.min(rewards):.4f}  max: {np.max(rewards):.4f}")
    print("  all rewards finite: OK")
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
