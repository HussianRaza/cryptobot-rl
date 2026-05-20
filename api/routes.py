"""FastAPI route handlers for the 5 API endpoints."""
import os
import json
import time
import urllib.request
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Request

from api import cache as cache_store
from api.schemas import (
    BacktestResponse, CompareResponse, CompareRow,
    TrainingCurvesResponse, PortfolioHistoryResponse, DisclaimerResponse,
    PaperTradingResponse, Metrics,
)
from baselines.buy_and_hold import BuyAndHold
from baselines.mean_reversion import MeanReversion
from baselines.momentum import Momentum
from baselines.random_agent import RandomAgent
from baselines.metrics import compute_all

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
    ohlcv_cols = ["open", "high", "low", "close", "volume"]
    means = df_train[ohlcv_cols].mean().to_dict()
    stds = {k: max(v, 1e-8) for k, v in df_train[ohlcv_cols].std().to_dict().items()}
    return {"means": means, "stds": stds}


def _equity_to_list(equity: pd.Series) -> list[dict]:
    return [{"date": str(d), "value": float(v)} for d, v in zip(equity.index, equity.values)]


def _sanitize_trade_log(trade_log: list) -> list:
    """Convert non-JSON-serializable values to plain Python types."""
    import numpy as np
    clean = []
    for entry in trade_log:
        sanitized = {}
        for k, v in entry.items():
            if isinstance(v, (pd.Timestamp, np.datetime64)) or hasattr(v, 'isoformat'):
                sanitized[k] = str(v)
            elif isinstance(v, np.integer):
                sanitized[k] = int(v)
            elif isinstance(v, np.floating):
                sanitized[k] = float(v)
            else:
                sanitized[k] = v
        clean.append(sanitized)
    return clean


def _run_ppo(asset: str, df_test: pd.DataFrame, train_stats: dict, request: Request):
    """Use preloaded PPO model from app state."""
    model_key = f"ppo_{asset}"
    agent = getattr(request.app.state, model_key, None)
    if agent is None:
        raise HTTPException(404, f"PPO model for {asset} not loaded. Run train_ppo.py first.")

    try:
        from env.crypto_trading_env import CryptoTradingEnv
        from env import SEED
    except ImportError as e:
        raise HTTPException(503, f"Gymnasium not installed ({e}). PPO inference unavailable.")

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
        trade_log=_sanitize_trade_log(trade_log),
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


COIN_IDS = {"btc": "bitcoin", "eth": "ethereum", "sol": "solana"}
PAPER_AGENTS = [k for k in AGENT_KEYS if k != "ppo"]


def _fetch_live_ohlcv(asset: str, days: int) -> pd.DataFrame:
    """Fetch daily OHLCV from CoinGecko (no API key required)."""
    coin = COIN_IDS[asset]
    url = (
        f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
        f"?vs_currency=usd&days={days}&interval=daily"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "cryptobot-rl/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        raise HTTPException(503, f"CoinGecko unavailable: {e}")

    prices = data["prices"]
    volumes = data.get("total_volumes", [])
    rows = []
    for i, (ts, close) in enumerate(prices):
        vol = volumes[i][1] if i < len(volumes) else 0.0
        rows.append({
            "date": pd.Timestamp(ts, unit="ms").normalize(),
            "open": close, "high": close, "low": close,
            "close": close, "volume": vol,
        })
    return pd.DataFrame(rows).drop_duplicates("date").reset_index(drop=True)


@router.get("/api/paper-trading", response_model=PaperTradingResponse)
async def paper_trading(
    asset: Annotated[str, Query()] = "btc",
    agent: Annotated[str, Query()] = "buy_hold",
    days: Annotated[int, Query()] = 60,
):
    if asset not in ASSETS:
        raise HTTPException(400, f"asset must be one of {ASSETS}")
    if agent not in PAPER_AGENTS:
        raise HTTPException(400, f"paper trading supports: {PAPER_AGENTS}")
    if not (7 <= days <= 365):
        raise HTTPException(400, "days must be between 7 and 365")

    # 5-minute cache bucket so live data refreshes periodically
    bucket = int(time.time() / 300)
    cache_key = ("paper_trading", asset, agent, days, bucket)
    cached = cache_store.get(cache_key)
    if cached:
        return cached

    df = _fetch_live_ohlcv(asset, days)
    initial_balance = 10_000.0
    trade_log, equity = _run_baseline(agent, df, initial_balance)
    metrics = compute_all(equity, trade_log)

    # Determine current signal: is strategy currently holding a position?
    buys = sum(1 for t in trade_log if t["type"] == "buy")
    sells = sum(1 for t in trade_log if t["type"] == "sell")
    current_signal = "long" if buys > sells else "flat"

    current_value = float(equity.iloc[-1])
    result = PaperTradingResponse(
        asset=asset,
        agent=agent,
        days=days,
        initial_balance=initial_balance,
        current_value=current_value,
        pnl_pct=(current_value - initial_balance) / initial_balance,
        current_signal=current_signal,
        metrics=Metrics(**metrics),
        equity_curve=_equity_to_list(equity),
        trade_log=_sanitize_trade_log(trade_log),
    )
    cache_store.set(cache_key, result)
    return result
