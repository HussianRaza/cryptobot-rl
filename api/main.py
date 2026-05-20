"""FastAPI app with CORS, model preload via lifespan, and route registration."""
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def _try_load_model(asset: str):
    """Load a trained PPO model if the zip exists, silently skip if SB3/model missing."""
    try:
        from agents.ppo_agent import PPOAgent
    except ImportError:
        print(f"  stable-baselines3 not installed — PPO models unavailable (baselines/data endpoints still work)")
        return None
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", f"ppo_{asset}_final.zip")
    if os.path.exists(model_path):
        print(f"  Loading PPO model for {asset}...")
        return PPOAgent.load(model_path)
    print(f"  PPO model for {asset} not found at {model_path} (train on Colab first)")
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading PPO models...")
    for asset in ["btc", "eth", "sol"]:
        setattr(app.state, f"ppo_{asset}", _try_load_model(asset))
    print("Startup complete.")
    yield
    print("Shutting down.")


app = FastAPI(
    title="Crypto RL Trading Bot API",
    description="Backtest PPO and classical strategies on BTC, ETH, SOL",
    version="1.0.0",
    lifespan=lifespan,
)

_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routes import router
app.include_router(router)
