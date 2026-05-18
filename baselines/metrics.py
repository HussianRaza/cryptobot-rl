"""Performance metrics shared by baselines and PPO evaluation.

Formulas adapted from FinRL finrl/agents/stablebaselines3/tune_sb3.py:120-126
All metrics hand-rolled — no quantstats dependency.
"""
import numpy as np
import pandas as pd

ANNUALIZATION = 252 ** 0.5


def sharpe_annualised(equity_curve: pd.Series, risk_free: float = 0.04) -> float:
    """Annualised Sharpe ratio from a daily equity curve."""
    returns = equity_curve.pct_change().dropna()
    if len(returns) < 2 or returns.std() < 1e-10:
        return 0.0
    rf_daily = risk_free / 252
    return float(ANNUALIZATION * (returns.mean() - rf_daily) / returns.std())


def max_drawdown(equity_curve: pd.Series) -> float:
    """Maximum drawdown as a positive fraction (0 = no drawdown, 1 = total loss)."""
    cummax = equity_curve.cummax()
    drawdowns = (cummax - equity_curve) / cummax.replace(0, np.nan)
    return float(drawdowns.max())


def total_return(equity_curve: pd.Series) -> float:
    """Total return as a decimal (0.1 = +10%)."""
    if equity_curve.iloc[0] == 0:
        return 0.0
    return float((equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0])


def win_rate(trade_log: list) -> float:
    """Fraction of closed trades with positive profit."""
    sell_trades = [t for t in trade_log if t.get("type") == "sell"]
    if not sell_trades:
        return 0.0
    wins = sum(1 for t in sell_trades if t.get("profits", 0) > 0)
    return float(wins / len(sell_trades))


def calmar(equity_curve: pd.Series) -> float:
    """Calmar ratio: annualised return / max drawdown."""
    ann_return = total_return(equity_curve) * (252 / max(len(equity_curve), 1))
    mdd = max_drawdown(equity_curve)
    if mdd < 1e-10:
        return 0.0
    return float(ann_return / mdd)


def compute_all(equity_curve: pd.Series, trade_log: list) -> dict:
    return {
        "sharpe": sharpe_annualised(equity_curve),
        "max_drawdown": max_drawdown(equity_curve),
        "total_return": total_return(equity_curve),
        "win_rate": win_rate(trade_log),
        "calmar": calmar(equity_curve),
    }
