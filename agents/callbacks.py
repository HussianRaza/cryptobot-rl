"""Training callbacks for PPO. TensorboardCallback adapted from FinRL."""
import statistics
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback


class MetricsCallback(BaseCallback):
    """Logs per-step reward and rollout stats to TensorBoard.

    Adapted from FinRL finrl/agents/stablebaselines3/models.py:34-76
    """

    def __init__(self, verbose=0):
        super().__init__(verbose)

    def _on_step(self) -> bool:
        try:
            reward = self.locals.get("rewards", self.locals.get("reward", [None]))[0]
            if reward is not None:
                self.logger.record("train/reward", float(reward))
        except Exception:
            pass
        return True

    def _on_rollout_end(self) -> bool:
        try:
            rollout_rewards = self.locals["rollout_buffer"].rewards.flatten()
            self.logger.record("train/reward_min", float(np.min(rollout_rewards)))
            self.logger.record("train/reward_mean", float(statistics.mean(rollout_rewards)))
            self.logger.record("train/reward_max", float(np.max(rollout_rewards)))
        except Exception:
            pass
        return True


def make_checkpoint_callback(save_path: str, save_freq: int = 10_000) -> CheckpointCallback:
    return CheckpointCallback(save_freq=save_freq, save_path=save_path, name_prefix="ppo")
