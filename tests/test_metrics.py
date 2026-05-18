"""Unit tests for baselines/metrics.py — no ML deps needed."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import pytest

from baselines.metrics import (
    sharpe_annualised, max_drawdown, total_return, win_rate, calmar, compute_all
)


def flat_equity(n=100, start=10_000):
    return pd.Series([float(start)] * n)


def growing_equity(n=252, start=10_000, end=12_000):
    return pd.Series(np.linspace(start, end, n))


def crash_equity():
    vals = list(np.linspace(10_000, 15_000, 50)) + list(np.linspace(15_000, 8_000, 50))
    return pd.Series(vals)


class TestSharpe:
    def test_flat_equity_is_zero(self):
        assert sharpe_annualised(flat_equity()) == 0.0

    def test_growing_equity_positive(self):
        s = sharpe_annualised(growing_equity())
        assert s > 0.0

    def test_single_element(self):
        assert sharpe_annualised(pd.Series([10_000])) == 0.0


class TestMaxDrawdown:
    def test_growing_has_zero_dd(self):
        assert max_drawdown(growing_equity()) == pytest.approx(0.0, abs=1e-6)

    def test_crash_dd(self):
        dd = max_drawdown(crash_equity())
        assert 0.4 < dd < 0.6  # ~46% drawdown

    def test_flat_zero(self):
        assert max_drawdown(flat_equity()) == 0.0


class TestTotalReturn:
    def test_growing(self):
        tr = total_return(growing_equity(start=10_000, end=12_000))
        assert tr == pytest.approx(0.2, rel=1e-4)

    def test_flat_zero(self):
        assert total_return(flat_equity()) == 0.0

    def test_loss(self):
        assert total_return(pd.Series([10_000, 8_000])) == pytest.approx(-0.2)


class TestWinRate:
    def test_all_wins(self):
        trades = [{"type": "sell", "profits": 100}, {"type": "sell", "profits": 200}]
        assert win_rate(trades) == 1.0

    def test_no_sells(self):
        trades = [{"type": "buy", "profits": 0}]
        assert win_rate(trades) == 0.0

    def test_half(self):
        trades = [{"type": "sell", "profits": 100}, {"type": "sell", "profits": -50}]
        assert win_rate(trades) == 0.5


class TestComputeAll:
    def test_returns_all_keys(self):
        result = compute_all(growing_equity(), [])
        assert set(result.keys()) == {"sharpe", "max_drawdown", "total_return", "win_rate", "calmar"}

    def test_all_finite(self):
        result = compute_all(crash_equity(), [])
        for k, v in result.items():
            assert np.isfinite(v), f"{k} is not finite: {v}"
