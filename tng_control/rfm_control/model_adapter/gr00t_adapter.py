from collections.abc import Sequence

from tng_control.rfm_control.model_adapter.mapper.model_output_mapper import ModelOutputMapper
from tng_control.domain_model.robot_action import RobotAction
from tng_control.rfm_control.model_adapter.model_port import ModelPort, ObservationHandler
from tng_control.config.model_configs.gr00t_config import Gr00tConfig
from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_client import Gr00tClient


class Gr00tAdapter(ModelPort):

    @property
    def model_output_mapper(self) -> ModelOutputMapper:
        return self._model_output_mapper

    @property
    def model_client(self) -> Gr00tClient:
        return self._model_client

    def __init__(self, config: Gr00tConfig, model_client: Gr00tClient,
                 model_output_mapper: ModelOutputMapper,
                 observation_handler: Sequence[ObservationHandler]) -> None:
        super().__init__(config, observation_handler)
        self._model_output_mapper = model_output_mapper
        self._model_client = model_client

    def get_action(self, prompt: str) -> Sequence[RobotAction]:
        observation = self.get_concat_observation()
        action = self.model_client.get_action(observation, prompt)
        return self.model_output_mapper.to_action(action)
