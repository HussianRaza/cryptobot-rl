"""PPO agent wrapper around stable-baselines3.

Hyperparameters aligned with FinRL's validated trading config
(finrl/config.py + finrl/agents/stablebaselines3/models.py:125-152).
"""
import os
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CallbackList

from agents.callbacks import MetricsCallback, make_checkpoint_callback
from env import SEED

PPO_HYPERPARAMS = dict(
    policy="MlpPolicy",
    n_steps=2048,
    batch_size=64,
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
)


class PPOAgent:
    """Thin wrapper providing build/train/save/load/predict."""

    def __init__(self):
        self.model: PPO = None

    def build(self, env_factory, n_envs: int = 4) -> "PPOAgent":
        """Create model with vectorised environment.

        env_factory: zero-arg callable that returns a CryptoTradingEnv instance
        """
        vec_env = make_vec_env(env_factory, n_envs=n_envs, vec_env_cls=DummyVecEnv, seed=SEED)
        self.model = PPO(env=vec_env, **PPO_HYPERPARAMS)
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
