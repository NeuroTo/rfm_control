from collections.abc import Sequence
import numpy as np
from typing_extensions import override

from tng_control.rfm_control.model_adapter.mapper.model_output_mapper import ModelOutputMapper
from tng_control.rfm_control.domain_model.robot_action import RobotAction
from tng_control.rfm_control.model_adapter.model_port import ModelPort
from tng_control.rfm_control.model_adapter.model_clients.octo.octo_model_client import OctoModelClient, OctoAction
from tng_control.rfm_control.observation_handler.observation_handler import ObservationHandler


class OctoAdapter(ModelPort):

    @property
    @override
    def model_output_mapper(self) -> ModelOutputMapper:
        return self._model_output_mapper

    @property
    @override
    def model_client(self) -> OctoModelClient:
        return self._model_client

    def __init__(self, model_client: OctoModelClient,
                 model_output_mapper: ModelOutputMapper,
                 observation_handler: Sequence[ObservationHandler]) -> None:
        super().__init__(observation_handler)
        self._model_output_mapper = model_output_mapper
        self._model_client = model_client

    @override
    def get_action(self, prompt: str) -> Sequence[RobotAction]:
        observation_dict: dict[str, np.ndarray] = self.get_concat_observation()
        observation_dict["timestep_pad_mask"] = np.array([[True]])
        action: OctoAction = self.model_client.get_action(observation_dict, prompt)

        return self.model_output_mapper.to_action(action)
