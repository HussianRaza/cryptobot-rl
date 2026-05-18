"""CryptoTradingEnv — Gymnasium single-asset trading environment.

Adapted from RLTrader (TradingEnv.py) with:
  - gym → gymnasium migration (reset/step API, 5-tuple step return)
  - Discrete(5) actions replacing Discrete(24)
  - Rolling-Sharpe reward (hand-rolled in env/reward.py)
  - Flattened Box observation (50-candle OHLCV + indicators + portfolio state)
"""
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

from env.reward import rolling_sharpe_reward
from env import SEED

OHLCV_COLS = ["open", "high", "low", "close", "volume"]
INDICATOR_COLS = ["rsi", "macd_diff", "bb_width", "ema50_dist", "vol_zscore"]

# Action constants
ACT_BUY_25 = 0
ACT_BUY_50 = 1
ACT_HOLD = 2
ACT_SELL_25 = 3
ACT_SELL_50 = 4

ACTION_FRACTIONS = {
    ACT_BUY_25: 0.25,
    ACT_BUY_50: 0.50,
    ACT_HOLD: 0.0,
    ACT_SELL_25: 0.25,
    ACT_SELL_50: 0.50,
}

WINDOW_SIZE = 50
N_PORTFOLIO_FEATURES = 5  # position, net_worth_norm, unrealized_pnl, peak_pct, var5


class CryptoTradingEnv(gym.Env):
    """Single-asset crypto trading environment for BTC, ETH, or SOL."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        df: pd.DataFrame,
        initial_balance: float = 10_000.0,
        window_size: int = WINDOW_SIZE,
        scaler_stats: dict = None,
    ):
        super().__init__()

        self.df = df.reset_index(drop=False)
        self.initial_balance = initial_balance
        self.window_size = window_size

        # OHLCV z-score stats — fit on train split only, applied universally
        if scaler_stats is None:
            self._ohlcv_mean = self.df[OHLCV_COLS].mean()
            self._ohlcv_std = self.df[OHLCV_COLS].std().replace(0.0, 1.0)
        else:
            self._ohlcv_mean = pd.Series(scaler_stats["means"], index=OHLCV_COLS)
            self._ohlcv_std = pd.Series(scaler_stats["stds"], index=OHLCV_COLS)

        # Observation: window_size * 5 OHLCV + 5 indicators + 5 portfolio
        n_obs = window_size * len(OHLCV_COLS) + len(INDICATOR_COLS) + N_PORTFOLIO_FEATURES
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(n_obs,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(5)

        self._start_step = window_size  # first step where full window is available
        self._end_step = len(self.df) - 1

    # ------------------------------------------------------------------
    # Gymnasium API
    # ------------------------------------------------------------------

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.current_step = self._start_step
        self.balance = float(self.initial_balance)
        self.asset_held = 0.0
        self.net_worths = [self.initial_balance]
        self.peak_value = self.initial_balance
        self.trades = []

        obs = self._get_observation()
        return obs, {}

    def step(self, action: int):
        trade_notional = self._take_action(action)

        self.current_step += 1

        current_price = float(self.df.loc[self.current_step, "close"])
        net_worth = self.balance + self.asset_held * current_price
        self.net_worths.append(net_worth)
        self.peak_value = max(self.peak_value, net_worth)

        reward = rolling_sharpe_reward(self.net_worths, self.peak_value, trade_notional)

        terminated = net_worth < 0.5 * self.initial_balance
        truncated = self.current_step >= self._end_step

        obs = self._get_observation()
        info = {
            "net_worth": net_worth,
            "balance": self.balance,
            "asset_held": self.asset_held,
            "step": self.current_step,
        }
        return obs, reward, terminated, truncated, info

    def render(self):
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _take_action(self, action: int) -> float:
        """Execute trade and return traded notional (for tx cost)."""
        current_price = float(self.df.loc[self.current_step, "close"])
        fraction = ACTION_FRACTIONS[action]
        trade_notional = 0.0

        if action in (ACT_BUY_25, ACT_BUY_50):
            spend = self.balance * fraction
            if spend > 1e-3:
                units = spend / current_price
                self.asset_held += units
                self.balance -= spend
                trade_notional = spend
                self.trades.append({
                    "Date": self.df.loc[self.current_step, "date"]
                    if "date" in self.df.columns else self.current_step,
                    "Close": current_price,
                    "total": spend,
                    "type": "buy",
                    "Net_worth": self.balance + self.asset_held * current_price,
                    "profits": 0.0,
                })

        elif action in (ACT_SELL_25, ACT_SELL_50):
            units = self.asset_held * fraction
            if units > 1e-8:
                proceeds = units * current_price
                self.asset_held -= units
                self.balance += proceeds
                trade_notional = proceeds
                self.trades.append({
                    "Date": self.df.loc[self.current_step, "date"]
                    if "date" in self.df.columns else self.current_step,
                    "Close": current_price,
                    "total": proceeds,
                    "type": "sell",
                    "Net_worth": self.balance + self.asset_held * current_price,
                    "profits": proceeds - (units * self._avg_cost()),
                })

        return trade_notional

    def _avg_cost(self) -> float:
        buy_trades = [t for t in self.trades if t["type"] == "buy"]
        if not buy_trades:
            return 0.0
        total_spent = sum(t["total"] for t in buy_trades)
        total_units = sum(t["total"] / t["Close"] for t in buy_trades)
        return total_spent / total_units if total_units > 1e-8 else 0.0

    def _get_observation(self) -> np.ndarray:
        """Build the flattened observation vector."""
        # 50-bar OHLCV window (z-scored with train stats)
        start = self.current_step - self.window_size
        end = self.current_step
        window = self.df.loc[start:end - 1, OHLCV_COLS].copy()

        # Pad if window is smaller than expected (shouldn't happen after _start_step)
        if len(window) < self.window_size:
            pad = pd.DataFrame(
                np.zeros((self.window_size - len(window), len(OHLCV_COLS))),
                columns=OHLCV_COLS,
            )
            window = pd.concat([pad, window], ignore_index=True)

        ohlcv_z = ((window - self._ohlcv_mean) / self._ohlcv_std).values.flatten()

        # Current-bar indicators
        row = self.df.loc[self.current_step]
        indicators = np.array([row[c] for c in INDICATOR_COLS], dtype=np.float32)

        # Portfolio state
        current_price = float(row["close"])
        net_worth = self.balance + self.asset_held * current_price

        # Position normalised to {-1, 0, 1} domain (we only go long or flat here)
        position = 1.0 if self.asset_held > 1e-8 else 0.0
        net_worth_norm = net_worth / self.initial_balance - 1.0
        unrealized_pnl = (self.asset_held * current_price) / (net_worth + 1e-8)
        peak_pct = net_worth / (self.peak_value + 1e-8) - 1.0

        # VaR(5%) — 5th percentile of 20-day return distribution
        returns_window = self.net_worths[-20:] if len(self.net_worths) >= 20 else self.net_worths
        if len(returns_window) >= 2:
            rets = np.diff(returns_window) / (np.array(returns_window[:-1]) + 1e-8)
            var5 = float(np.percentile(rets, 5))
        else:
            var5 = 0.0

        portfolio = np.array([position, net_worth_norm, unrealized_pnl, peak_pct, var5], dtype=np.float32)

        obs = np.concatenate([ohlcv_z.astype(np.float32), indicators, portfolio])
        obs = np.where(np.isfinite(obs), obs, 0.0).astype(np.float32)
        return obs
