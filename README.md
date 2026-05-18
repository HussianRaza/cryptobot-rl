# Crypto RL Trading Bot

A reinforcement learning trading bot for BTC, ETH, and SOL using PPO (Proximal Policy Optimization) with a custom Gymnasium environment, four classical baselines, a FastAPI backend, and a React dashboard.

**Educational project. Not financial advice. See [DISCLAIMER.md](DISCLAIMER.md).**

---

## Architecture

| Layer | Stack |
|---|---|
| Data | yfinance → CSV → `ta` indicators → per-split feature CSVs |
| Environment | Gymnasium `CryptoTradingEnv`, `Discrete(5)` actions, rolling-Sharpe reward |
| Agent | Stable-Baselines3 PPO, MlpPolicy [128, 128] |
| Baselines | Buy-and-hold, Mean reversion, Momentum, Random |
| API | FastAPI on port 8000 |
| UI | React + Vite + Plotly.js on port 3000 |

---

## Setup

### Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

---

## Data Pipeline

```bash
# Download 2020–2024 daily OHLCV (BTC, ETH, SOL)
python scripts/download_data.py --assets btc eth sol

# Compute indicators per split (train/val/test — no lookahead)
python scripts/compute_indicators.py

# Verify
python -c "import pandas as pd; df=pd.read_csv('data/processed/btc_features.csv'); print(df.shape, df.isna().sum().sum())"
```

---

## Training (Google Colab)

Training runs on Google Colab (free CPU/T4 GPU). See [`notebooks/train_colab.ipynb`](notebooks/train_colab.ipynb).

1. Open the notebook in Colab
2. Update `REPO_URL` with your GitHub repo URL
3. Run all cells — trains BTC, ETH, SOL sequentially (~20–60 min each on T4)
4. Download the three `.zip` model files and place them in `models/`

Pre-trained models (after Colab run):
```
models/ppo_btc_final.zip
models/ppo_eth_final.zip
models/ppo_sol_final.zip
```

---

## Baseline Evaluation (local)

```bash
python scripts/run_baselines.py --asset btc --year 2024
```

Full evaluation (requires trained PPO model):
```bash
python scripts/evaluate.py --asset btc
# outputs: results/comparison_2024.csv, results/equity_curves.png
```

---

## Running the App

### Backend

```bash
uvicorn api.main:app --reload --port 8000
```

Endpoints:
- `GET /api/backtest?asset=btc&agent=ppo`
- `GET /api/compare?asset=btc`
- `GET /api/training-curves?asset=btc`
- `GET /api/portfolio-history?asset=btc&agent=ppo`
- `GET /api/disclaimer`

### Frontend

```bash
cd frontend && npm run dev   # http://localhost:3000
```

---

## Tests

```bash
pytest tests/ -v
# test_metrics.py and test_baselines.py run without SB3
# test_env.py requires gymnasium installed
```

---

## Results

After training and running evaluation, results are saved to `results/`:
- `comparison_2024.csv` — Sharpe, max DD, total return, win rate, Calmar for all 5 strategies
- `equity_curves.png` — portfolio value over 2024 test period

---

## Reproducibility

All experiments use `SEED = 42` (defined in `env/__init__.py`). The random baseline uses `np.random.default_rng(42)`.

Splits:
- **Train**: 2020-01-01 → 2022-12-31
- **Val**: 2023-01-01 → 2023-12-31
- **Test**: 2024-01-01 → 2024-12-31

---

## Future Work

- SAC agent (Soft Actor-Critic) for comparison
- Hyperparameter sweep via Optuna
- Live paper-trading mode

---

## Disclosure

See [docs/ai_disclosure.md](docs/ai_disclosure.md) for reference repositories and AI assistance disclosure.
