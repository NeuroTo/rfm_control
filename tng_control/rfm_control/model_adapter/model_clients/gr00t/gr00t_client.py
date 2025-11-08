import numpy as np
from typing_extensions import override

from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_robot_inference_client import RobotInferenceClient
from tng_control.config.model_configs.gr00t_config import Gr00tConfig
from tng_control.rfm_control.model_adapter.model_clients.model_client import ModelClient


class Gr00tClient(ModelClient):
    """Policy client implementation for GR00T robot models using configuration objects."""

    def __init__(self, config: Gr00tConfig):
        """
        Initialize with configuration dictionary.

        Args:
            config: Configuration object for the policy client.
        """
        self.policy_client = RobotInferenceClient(port=config.port)

    @override
    def get_action(self, observation: dict[str, np.ndarray], prompt: str) -> dict[str, np.ndarray]:
        """Get action from GR00T model."""

        input_dict: dict[str, np.ndarray | list[str]] = dict(observation)
        input_dict["annotation.human.action.task_description"] = [prompt]
        return self.policy_client.get_action(input_dict)
