"""FastAPI route handlers for the 5 API endpoints."""
import os
import json
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Request

from api import cache as cache_store
from api.schemas import (
    BacktestResponse, CompareResponse, CompareRow,
    TrainingCurvesResponse, PortfolioHistoryResponse, DisclaimerResponse,
    Metrics,
)
from baselines.buy_and_hold import BuyAndHold
from baselines.mean_reversion import MeanReversion
from baselines.momentum import Momentum
from baselines.random_agent import RandomAgent
from baselines.metrics import compute_all
from env.crypto_trading_env import CryptoTradingEnv, OHLCV_COLS
from env import SEED

router = APIRouter()

ASSETS = ["btc", "eth", "sol"]
AGENT_KEYS = ["ppo", "buy_hold", "mean_rev", "momentum", "random"]

BASELINE_MAP = {
    "buy_hold": BuyAndHold,
    "mean_rev": MeanReversion,
    "momentum": Momentum,
    "random": RandomAgent,
}

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def _processed_path(asset: str) -> str:
    return os.path.join(BASE_DIR, "data", "processed", f"{asset}_features.csv")


def _load_split(asset: str, split: str) -> pd.DataFrame:
    df = pd.read_csv(_processed_path(asset), index_col=0, parse_dates=True)
    result = df[df["split"] == split].copy()
    return result.reset_index().rename(columns={"index": "date"})


def _train_stats(df_train: pd.DataFrame) -> dict:
    means = df_train[OHLCV_COLS].mean().to_dict()
    stds = {k: max(v, 1e-8) for k, v in df_train[OHLCV_COLS].std().to_dict().items()}
    return {"means": means, "stds": stds}


def _equity_to_list(equity: pd.Series) -> list[dict]:
    return [{"date": str(d), "value": float(v)} for d, v in zip(equity.index, equity.values)]


def _run_ppo(asset: str, df_test: pd.DataFrame, train_stats: dict, request: Request):
    """Use preloaded PPO model from app state."""
    model_key = f"ppo_{asset}"
    agent = getattr(request.app.state, model_key, None)
    if agent is None:
        raise HTTPException(404, f"PPO model for {asset} not loaded. Run train_ppo.py first.")

    env = CryptoTradingEnv(df_test.copy(), scaler_stats=train_stats)
    obs, _ = env.reset(seed=SEED)
    portfolio_values = [10_000.0]
    done = False
    while not done:
        action = agent.predict(obs)
        obs, reward, terminated, truncated, info = env.step(int(action))
        portfolio_values.append(info["net_worth"])
        done = terminated or truncated

    dates = df_test["date"].values[:len(portfolio_values)]
    equity = pd.Series(portfolio_values[:len(dates)], index=dates, name="ppo")
    return env.trades, equity


def _run_baseline(agent_key: str, df_test: pd.DataFrame, initial_balance: float = 10_000.0):
    strategy = BASELINE_MAP[agent_key]()
    return strategy.run(df_test.copy(), initial_balance=initial_balance)


@router.get("/api/backtest", response_model=BacktestResponse)
async def backtest(
    request: Request,
    asset: Annotated[str, Query()] = "btc",
    agent: Annotated[str, Query()] = "ppo",
):
    if asset not in ASSETS:
        raise HTTPException(400, f"asset must be one of {ASSETS}")
    if agent not in AGENT_KEYS:
        raise HTTPException(400, f"agent must be one of {AGENT_KEYS}")

    cache_key = ("backtest", asset, agent)
    cached = cache_store.get(cache_key)
    if cached:
        return cached

    df_train = _load_split(asset, "train")
    df_test = _load_split(asset, "test")
    train_stats = _train_stats(df_train)

    if agent == "ppo":
        trade_log, equity = _run_ppo(asset, df_test, train_stats, request)
    else:
        trade_log, equity = _run_baseline(agent, df_test)

    metrics = compute_all(equity, trade_log)
    result = BacktestResponse(
        metrics=Metrics(**metrics),
        trade_log=trade_log,
        equity_curve=_equity_to_list(equity),
    )
    cache_store.set(cache_key, result)
    return result


@router.get("/api/compare", response_model=CompareResponse)
async def compare(
    request: Request,
    asset: Annotated[str, Query()] = "btc",
):
    if asset not in ASSETS:
        raise HTTPException(400, f"asset must be one of {ASSETS}")

    cache_key = ("compare", asset, "all")
    cached = cache_store.get(cache_key)
    if cached:
        return cached

    df_train = _load_split(asset, "train")
    df_test = _load_split(asset, "test")
    train_stats = _train_stats(df_train)

    rows = []
    for agent_key in AGENT_KEYS:
        try:
            if agent_key == "ppo":
                trade_log, equity = _run_ppo(asset, df_test, train_stats, request)
            else:
                trade_log, equity = _run_baseline(agent_key, df_test)
            metrics = compute_all(equity, trade_log)
            rows.append(CompareRow(strategy=agent_key, **metrics))
        except HTTPException:
            pass

    result = CompareResponse(asset=asset, rows=rows)
    cache_store.set(cache_key, result)
    return result


@router.get("/api/training-curves", response_model=TrainingCurvesResponse)
async def training_curves(asset: Annotated[str, Query()] = "btc"):
    """Return episode reward series from saved training curves JSON."""
    if asset not in ASSETS:
        raise HTTPException(400, f"asset must be one of {ASSETS}")

    curves_path = os.path.join(BASE_DIR, "results", f"training_curves_{asset}.json")
    if not os.path.exists(curves_path):
        return TrainingCurvesResponse(asset=asset, episodes=[], rewards=[])

    with open(curves_path) as f:
        data = json.load(f)

    return TrainingCurvesResponse(
        asset=asset,
        episodes=data.get("episodes", []),
        rewards=data.get("rewards", []),
    )


@router.get("/api/portfolio-history", response_model=PortfolioHistoryResponse)
async def portfolio_history(
    request: Request,
    asset: Annotated[str, Query()] = "btc",
    agent: Annotated[str, Query()] = "ppo",
):
    if asset not in ASSETS:
        raise HTTPException(400, f"asset must be one of {ASSETS}")
    if agent not in AGENT_KEYS:
        raise HTTPException(400, f"agent must be one of {AGENT_KEYS}")

    cache_key = ("portfolio_history", asset, agent)
    cached = cache_store.get(cache_key)
    if cached:
        return cached

    df_train = _load_split(asset, "train")
    df_test = _load_split(asset, "test")
    train_stats = _train_stats(df_train)

    if agent == "ppo":
        _, equity = _run_ppo(asset, df_test, train_stats, request)
    else:
        _, equity = _run_baseline(agent, df_test)

    result = PortfolioHistoryResponse(
        asset=asset,
        agent=agent,
        dates=[str(d) for d in equity.index],
        values=[float(v) for v in equity.values],
    )
    cache_store.set(cache_key, result)
    return result


@router.get("/api/disclaimer", response_model=DisclaimerResponse)
async def disclaimer():
    disclaimer_path = os.path.join(BASE_DIR, "DISCLAIMER.md")
    if not os.path.exists(disclaimer_path):
        return DisclaimerResponse(text="No disclaimer found.")
    with open(disclaimer_path) as f:
        return DisclaimerResponse(text=f.read())
