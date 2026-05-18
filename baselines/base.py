"""BaselineStrategy abstract base class."""
from abc import ABC, abstractmethod
import pandas as pd


class BaselineStrategy(ABC):
    """All baseline strategies implement this interface."""

    @abstractmethod
    def run(self, df: pd.DataFrame, initial_balance: float = 10_000.0) -> tuple:
        """Execute strategy on df and return (trade_log, equity_curve).

        trade_log: list of dicts with keys {Date, Close, total, type, Net_worth, profits}
        equity_curve: pd.Series of portfolio value indexed by date
        """
