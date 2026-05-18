"""Pydantic response models for the backtest API."""
from typing import Any
from pydantic import BaseModel


class Metrics(BaseModel):
    sharpe: float
    max_drawdown: float
    total_return: float
    win_rate: float
    calmar: float


class BacktestResponse(BaseModel):
    metrics: Metrics
    trade_log: list[dict[str, Any]]
    equity_curve: list[dict[str, Any]]  # [{date, value}]


class CompareRow(BaseModel):
    strategy: str
    sharpe: float
    max_drawdown: float
    total_return: float
    win_rate: float
    calmar: float


class CompareResponse(BaseModel):
    asset: str
    rows: list[CompareRow]


class TrainingCurvesResponse(BaseModel):
    asset: str
    episodes: list[int]
    rewards: list[float]


class PortfolioHistoryResponse(BaseModel):
    asset: str
    agent: str
    dates: list[str]
    values: list[float]


class DisclaimerResponse(BaseModel):
    text: str
