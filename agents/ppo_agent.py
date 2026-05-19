"""PPO agent wrapper around stable-baselines3.

Hyperparameters aligned with FinRL's validated trading config
(finrl/config.py + finrl/agents/stablebaselines3/models.py:125-152).
"""
import os
import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import CallbackList

from agents.callbacks import MetricsCallback, make_checkpoint_callback
from env import SEED

# Use GPU when available (T4 on Colab), fall back to CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

PPO_HYPERPARAMS = dict(
    policy="MlpPolicy",
    n_steps=2048,
    batch_size=256,
    n_epochs=10,
    learning_rate=2.5e-4,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.01,
    vf_coef=0.5,
    policy_kwargs=dict(net_arch=[128, 128]),
    tensorboard_log="logs/tb/",
    seed=SEED,
    verbose=1,
    device=DEVICE,
)


class PPOAgent:
    """Thin wrapper providing build/train/save/load/predict."""

    def __init__(self):
        self.model: PPO = None

    def build(
        self,
        env_factory,
        n_envs: int = 4,
        n_steps: int = None,
        batch_size: int = None,
        use_subproc: bool = False,
    ) -> "PPOAgent":
        """Create model with vectorised environment.

        env_factory: zero-arg callable that returns a CryptoTradingEnv instance
        use_subproc: use SubprocVecEnv for true CPU parallelism (recommended on Colab T4)
        """
        vec_cls = SubprocVecEnv if use_subproc and n_envs > 1 else DummyVecEnv
        vec_env = make_vec_env(env_factory, n_envs=n_envs, vec_env_cls=vec_cls, seed=SEED)
        hyperparams = {**PPO_HYPERPARAMS}
        if n_steps is not None:
            hyperparams["n_steps"] = n_steps
        if batch_size is not None:
            hyperparams["batch_size"] = batch_size
        self.model = PPO(env=vec_env, **hyperparams)
        return self

    def train(
        self,
        timesteps: int = 500_000,
        checkpoint_dir: str = "models/checkpoints/",
    ) -> "PPOAgent":
        if self.model is None:
            raise RuntimeError("Call build() before train()")
        os.makedirs(checkpoint_dir, exist_ok=True)
        callbacks = CallbackList([
            MetricsCallback(),
            make_checkpoint_callback(checkpoint_dir),
        ])
        self.model.learn(total_timesteps=timesteps, callback=callbacks, reset_num_timesteps=False)
        return self

    def save(self, path: str) -> None:
        self.model.save(path)

    @classmethod
    def load(cls, path: str, env=None) -> "PPOAgent":
        agent = cls()
        agent.model = PPO.load(path, env=env)
        return agent

    def predict(self, obs: np.ndarray, deterministic: bool = True):
        action, _ = self.model.predict(obs, deterministic=deterministic)
        return action
