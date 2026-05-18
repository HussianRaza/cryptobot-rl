"""Tests for CryptoTradingEnv — no SB3 needed for basic shape checks."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import pytest

from env.crypto_trading_env import CryptoTradingEnv, WINDOW_SIZE


def make_env_df(n=300):
    """Minimal feature DataFrame with required columns."""
    dates = pd.date_range("2020-01-01", periods=n, freq="D")
    prices = np.linspace(10_000, 15_000, n)
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "date": dates,
        "open": prices,
        "high": prices * 1.01,
        "low": prices * 0.99,
        "close": prices,
        "volume": rng.uniform(1e8, 1e9, n),
        "rsi": rng.uniform(20, 80, n),
        "macd_diff": rng.uniform(-500, 500, n),
        "bb_width": rng.uniform(0.01, 0.1, n),
        "ema50_dist": rng.uniform(-0.05, 0.05, n),
        "vol_zscore": rng.standard_normal(n),
        "split": ["train"] * n,
    })


class TestEnvInit:
    def test_obs_space_shape(self):
        env = CryptoTradingEnv(make_env_df())
        expected = WINDOW_SIZE * 5 + 5 + 5  # OHLCV + indicators + portfolio
        assert env.observation_space.shape == (expected,)

    def test_action_space_size(self):
        env = CryptoTradingEnv(make_env_df())
        assert env.action_space.n == 5


class TestEnvReset:
    def test_returns_tuple(self):
        env = CryptoTradingEnv(make_env_df())
        result = env.reset(seed=42)
        assert isinstance(result, tuple) and len(result) == 2

    def test_obs_correct_shape(self):
        env = CryptoTradingEnv(make_env_df())
        obs, _ = env.reset(seed=42)
        assert obs.shape == env.observation_space.shape

    def test_obs_all_finite(self):
        env = CryptoTradingEnv(make_env_df())
        obs, _ = env.reset(seed=42)
        assert np.all(np.isfinite(obs))


class TestEnvStep:
    def test_step_returns_5_tuple(self):
        env = CryptoTradingEnv(make_env_df())
        env.reset(seed=42)
        result = env.step(2)  # hold
        assert len(result) == 5

    def test_reward_is_finite(self):
        env = CryptoTradingEnv(make_env_df())
        env.reset(seed=42)
        for _ in range(50):
            _, reward, terminated, truncated, _ = env.step(env.action_space.sample())
            assert np.isfinite(reward), f"non-finite reward: {reward}"
            if terminated or truncated:
                break

    def test_all_actions_valid(self):
        for action in range(5):
            env = CryptoTradingEnv(make_env_df())
            env.reset(seed=42)
            obs, reward, terminated, truncated, info = env.step(action)
            assert obs.shape == env.observation_space.shape

    def test_balance_nonnegative(self):
        env = CryptoTradingEnv(make_env_df())
        env.reset(seed=42)
        for _ in range(100):
            _, _, terminated, truncated, info = env.step(env.action_space.sample())
            assert info["balance"] >= 0
            if terminated or truncated:
                break
