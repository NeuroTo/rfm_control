from collections.abc import Sequence
import numpy as np
from tng_control.rfm_control.model_adapter.mapper.model_output_mapper import ModelOutputMapper
from tng_control.domain_model.robot_action import RobotAction
from tng_control.config.model_configs.octo_config import OctoConfig
from tng_control.rfm_control.model_adapter.model_port import ModelPort
from tng_control.rfm_control.model_adapter.model_clients.octo.octo_client import OctoClient
from tng_control.rfm_control.model_adapter.observation_handler.image_handler import ObservationHandler


class OctoAdapter(ModelPort):

    @property
    def model_output_mapper(self) -> ModelOutputMapper:
        return self._model_output_mapper

    @property
    def model_client(self) -> OctoClient:
        return self._model_client

    def __init__(self, config: OctoConfig, model_client: OctoClient,
                 model_output_mapper: ModelOutputMapper,
                 observation_handler: Sequence[ObservationHandler]) -> None:
        super().__init__(config, observation_handler)
        self._model_output_mapper = model_output_mapper
        self._model_client = model_client

    def get_action(self, prompt: str) -> Sequence[RobotAction]:
        observation_dict: dict[str, np.ndarray] = self.get_concat_observation()
        observation_dict["timestep_pad_mask"] = np.array([[True]])
        action: list[list[list[float]]] = self.model_client.get_action(observation_dict, prompt)

        return self.model_output_mapper.to_action(action)
