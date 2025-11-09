from abc import ABC, abstractmethod
from collections.abc import Sequence
import numpy as np

from tng_control.rfm_control.model_adapter.mapper.model_output_mapper import ModelOutputMapper
from tng_control.rfm_control.domain_model.robot_action import RobotAction
from tng_control.rfm_control.model_adapter.model_clients.model_client import ModelClient
from tng_control.rfm_control.model_adapter.observation_handler.image_handler import ObservationHandler


class ModelPort(ABC):
    """
    Interface for parsing the observation (joint state and images)
    to the format expected by the policy client.
    """

    @property
    @abstractmethod
    def model_client(self) -> ModelClient:
        pass

    @property
    @abstractmethod
    def model_output_mapper(self) -> ModelOutputMapper:
        pass

    @property
    def observation_handler(self) -> Sequence[ObservationHandler]:
        return self._observation_handler

    def __init__(self, observation_handler: Sequence[ObservationHandler]):
        self._observation_handler = observation_handler

    @abstractmethod
    def get_action(self, prompt: str) -> Sequence[RobotAction]:
        pass

    def get_concat_observation(self) -> dict[str, np.ndarray]:
        observation_dict = {}
        for observation_handler in self._observation_handler:
            observation_dict |= observation_handler.get_observation_dict()
        return observation_dict
