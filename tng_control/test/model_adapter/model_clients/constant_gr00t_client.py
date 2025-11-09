import time
import numpy as np

from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_robot_inference_client import RobotInferenceClient
from tng_control.rfm_control.config.model_configs.gr00t_config import Gr00tConfig
from tng_control.rfm_control.model_adapter.model_clients.model_client import ModelClient


class ConstantGr00tClient(ModelClient):

    def __init__(self, config: Gr00tConfig):
        self.start_time = time.time()
        self.started = False
        self.positions = np.array([
            [0, 0, 0, 0, 0],
            [-50, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, -50, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, -50, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, -50, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, -50],
            [0, 0, 0, 0, 0]
        ])
        self.duration = 7

    def get_action(self, observation: dict[str, np.ndarray], prompt: str) -> dict[str, np.ndarray]:
        if not self.started:
            self.start_time = time.time()
            self.started = True
        elapsed_time = time.time() - self.start_time

        position_index = int(elapsed_time // self.duration) % len(self.positions)

        return {
            "action.single_arm": np.array([self.positions[position_index]]),
            "action.gripper": np.array([12.2]),
            "action.single_arm_velocity":
            np.array([[100, 100, 100, 100, 100]]),
            "action.gripper_velocity": np.array([50])}


class ConstantGr00tRTCClient(ModelClient):
    """Policy client implementation for GR00T robot models using configuration objects."""

    def __init__(self, config: Gr00tConfig):
        self.start_time = time.time()
        self.started = False

        self.positions = np.array([
            [0, 0, 0, 0, 0],
            [-50, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, -50, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, -50, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, -50, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, -50],
            [0, 0, 0, 0, 0],
        ])
        self.duration = 3

    def get_action(self, observation: dict[str, np.ndarray], prompt: str) -> dict[str, np.ndarray]:

        if not self.started:
            self.start_time = time.time()
            self.started = True
        elapsed_time = time.time() - self.start_time

        position_index = int(elapsed_time // self.duration) % len(self.positions)

        return {
            "action.single_arm": self.positions[position_index],
            "action.gripper": 12.2,
            "action.single_arm_velocity": np.array([100, 100, 100, 100, 100]),
            "action.gripper_velocity": 50}
