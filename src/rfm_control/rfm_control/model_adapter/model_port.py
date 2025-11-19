from abc import ABC, abstractmethod
from collections.abc import Sequence
import numpy as np

from rfm_control.model_adapter.mapper.input.model_input_mapper import ModelInputMapper
from rfm_control.model_adapter.mapper.output.model_output_mapper import ModelOutputMapper
from rfm_control.domain_model.robot_action import RobotAction
from rfm_control.model_adapter.model_clients.model_client import ModelClient
from rfm_control.observation_handler.observation_handler import ObservationHandler
from rfm_control.observation_handler.observation_dto import Observations, RobotState


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
    def model_input_mapper(self) -> ModelInputMapper:
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

    def get_concat_observation(self) -> Observations:
        """
        Get concatenated observations from all handlers.
        
        Returns an Observations object that will be transformed
        by the ModelInputMapper to model-specific format.
        
        Merges partial Observations from all handlers:
        - JointStateHandler provides robots
        - ImageHandler provides images
        """
        robots: list[RobotState] = []
        images: dict[str, np.ndarray] = {}
        
        for observation_handler in self._observation_handler:
            partial_obs = observation_handler.get_observations()
            
            # Merge robots from each handler
            robots.extend(partial_obs.robots)
            
            # Merge images from each handler
            images.update(partial_obs.images)
        
        return Observations(robots=robots, images=images)
