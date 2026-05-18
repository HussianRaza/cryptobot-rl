"""Rolling-Sharpe reward with drawdown penalty and transaction cost.

Hand-rolled — no reference repo has in-step rolling Sharpe.
Formula from FinRL: (252**0.5) * mean_return / std_return
"""
import numpy as np

ANNUALIZATION = 252 ** 0.5
RISK_FREE_DAILY = 0.04 / 252  # 4% annual risk-free rate
REWARD_WINDOW = 30
DD_THRESHOLD = 0.20  # drawdown penalty kicks in above 20%
DD_SCALE = 2.0
TX_COST_RATE = 0.001  # 0.1% per traded notional
REWARD_CLIP = 10.0


def rolling_sharpe_reward(
    net_worths: list,
    peak_value: float,
    trade_notional: float,
) -> float:
    """Compute one-step reward from portfolio history."""
    if len(net_worths) < 2:
        return 0.0

    window_values = net_worths[-REWARD_WINDOW:] if len(net_worths) >= REWARD_WINDOW else net_worths
    prev_values = np.array(window_values[:-1], dtype=np.float64)
    curr_values = np.array(window_values[1:], dtype=np.float64)

    # Avoid division by zero in return calculation
    safe_prev = np.where(np.abs(prev_values) < 1e-8, 1e-8, prev_values)
    returns = (curr_values - prev_values) / safe_prev

    mean_ret = float(np.mean(returns))
    std_ret = float(np.std(returns))

    if std_ret < 1e-8:
        sharpe = 0.0
    else:
        sharpe = ANNUALIZATION * (mean_ret - RISK_FREE_DAILY) / std_ret

    # Drawdown penalty
    current_value = net_worths[-1]
    safe_peak = peak_value if abs(peak_value) > 1e-8 else 1e-8
    drawdown = max(0.0, (peak_value - current_value) / safe_peak)
    dd_penalty = max(0.0, drawdown - DD_THRESHOLD) * DD_SCALE

    # Transaction cost
    tx_cost = TX_COST_RATE * trade_notional

    reward = sharpe - dd_penalty - tx_cost

    if not np.isfinite(reward):
        return 0.0
    return float(np.clip(reward, -REWARD_CLIP, REWARD_CLIP))
