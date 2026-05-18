"""Tests for baseline strategies — no ML deps needed."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import pytest

from baselines.buy_and_hold import BuyAndHold
from baselines.mean_reversion import MeanReversion
from baselines.momentum import Momentum
from baselines.random_agent import RandomAgent


def make_df(n=100, trend="up"):
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    if trend == "up":
        prices = np.linspace(10_000, 15_000, n)
    elif trend == "down":
        prices = np.linspace(15_000, 10_000, n)
    else:
        prices = 10_000 + 2000 * np.sin(np.linspace(0, 4 * np.pi, n))

    return pd.DataFrame({
        "date": dates,
        "open": prices,
        "high": prices * 1.01,
        "low": prices * 0.99,
        "close": prices,
        "volume": np.ones(n) * 1e9,
    })


class TestBuyAndHold:
    def test_equity_length(self):
        df = make_df()
        _, equity = BuyAndHold().run(df)
        assert len(equity) == len(df)

    def test_positive_return_on_uptrend(self):
        df = make_df(trend="up")
        trade_log, equity = BuyAndHold().run(df)
        assert equity.iloc[-1] > equity.iloc[0]

    def test_two_trades(self):
        df = make_df()
        trade_log, _ = BuyAndHold().run(df)
        assert len(trade_log) == 2


class TestMeanReversion:
    def test_equity_length(self):
        df = make_df(trend="oscillate")
        _, equity = MeanReversion().run(df)
        assert len(equity) == len(df)

    def test_no_negative_balance(self):
        df = make_df()
        _, equity = MeanReversion().run(df)
        assert (equity.values >= 0).all()


class TestMomentum:
    def test_equity_length(self):
        df = make_df()
        _, equity = Momentum().run(df)
        assert len(equity) == len(df)

    def test_no_negative_balance(self):
        df = make_df(trend="down")
        _, equity = Momentum().run(df)
        assert (equity.values >= 0).all()


class TestRandomAgent:
    def test_reproducible(self):
        df = make_df()
        _, eq1 = RandomAgent(seed=42).run(df)
        _, eq2 = RandomAgent(seed=42).run(df)
        assert list(eq1.values) == list(eq2.values)

    def test_different_seeds_differ(self):
        df = make_df(n=200)
        _, eq1 = RandomAgent(seed=42).run(df)
        _, eq2 = RandomAgent(seed=99).run(df)
        assert list(eq1.values) != list(eq2.values)

    def test_equity_length(self):
        df = make_df()
        _, equity = RandomAgent().run(df)
        assert len(equity) == len(df)
