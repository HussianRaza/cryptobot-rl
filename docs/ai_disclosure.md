# AI and Source Disclosure

## Reference Repositories

The following open-source repositories were studied and partially adapted during development:

| Repository | What Was Adapted |
|---|---|
| [notadamking/RLTrader](https://github.com/notadamking/RLTrader) | `CryptoTradingEnv` class structure, portfolio bookkeeping (`balance`, `asset_held`, `net_worths`, `trades` list), env reset/step skeleton. **Migrated from `gym` 0.21 to `gymnasium` 0.26+ API.** |
| [pythonlessons/RL-Bitcoin-trading-bot](https://github.com/pythonlessons/RL-Bitcoin-trading-bot) | Indicator computation pattern using the `ta` library (RSI, MACD, Bollinger Bands, EMA). PSAR dropped; volume z-score added. |
| [AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL) | PPO hyperparameter values (`learning_rate=2.5e-4`, `ent_coef=0.01`), `TensorboardCallback` pattern, `data_split()` helper, multi-strategy backtest aggregation pattern, Sharpe formula `(252**0.5) * mean / std`. |
| [roblen001/reinforcement_learning_trading_agent](https://github.com/roblen001/reinforcement_learning_trading_agent) | Trade log dict shape `{Date, Close, total, type, Net_worth, profits}`. Random baseline pattern — **seeded with `np.random.default_rng(42)` (original was not reproducible).** |
| [GioStamoulos/BTC_RL_Trading_Bot](https://github.com/GioStamoulos/BTC_RL_Trading_Bot) | Reward design reference (rolling-Sharpe concept). Final reward implementation hand-rolled — none of the reference repos have in-step rolling Sharpe. |

## Libraries

- **yfinance** — historical OHLCV data download
- **ta** — technical indicator computation
- **Stable-Baselines3** — PPO implementation and env checking
- **Gymnasium** — RL environment interface
- **FastAPI** — REST API backend
- **React + Vite + Plotly.js** — web dashboard

## AI Assistance

This project was developed with the assistance of **Claude Code** (Anthropic), an AI coding assistant.

Claude Code's role included:
- Implementation planning and architecture design
- Code scaffolding for all modules (env, agents, baselines, API, frontend)
- Debugging and fixing issues (yfinance MultiIndex columns, gymnasium migration, Sharpe edge cases)
- Writing tests and documentation

All generated code was reviewed, the gym→gymnasium migration was verified against the specification, and the backdating section of the original project brief was intentionally excluded as it would misrepresent the development timeline.
