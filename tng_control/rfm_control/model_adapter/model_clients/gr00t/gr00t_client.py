import numpy as np
from typing_extensions import override

from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_robot_inference_client import RobotInferenceClient
from tng_control.rfm_control.config.model_client_config_base import Gr00tConfigBase
from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_model_client import Gr00tModelClient, Gr00tAction


class Gr00tClient(Gr00tModelClient):
    """Policy client implementation for GR00T robot models using configuration objects."""

    def __init__(self, config: Gr00tConfigBase):
        """
        Initialize with configuration dictionary.

        Args:
            config: Configuration object for the policy client.
        """
        self._policy_client = RobotInferenceClient(port=config.port)

    @override
    def get_action(self, observation: dict[str, np.ndarray], prompt: str) -> Gr00tAction:
        """Get action from GR00T model."""

        input_dict: dict[str, np.ndarray | list[str]] = dict(observation)
        input_dict["annotation.human.action.task_description"] = [prompt]
        return self._policy_client.get_action(input_dict)
