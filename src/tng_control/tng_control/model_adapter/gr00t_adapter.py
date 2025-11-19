from collections.abc import Sequence
from typing_extensions import override

from tng_control.model_adapter.mapper.input.model_input_mapper import ModelInputMapper
from tng_control.model_adapter.mapper.output.model_output_mapper import ModelOutputMapper
from tng_control.domain_model.robot_action import RobotAction
from tng_control.model_adapter.model_port import ModelPort, ObservationHandler
from tng_control.model_adapter.model_clients.gr00t.gr00t_model_client import Gr00tModelClient


class Gr00tAdapter(ModelPort):

    @property
    @override
    def model_input_mapper(self) -> ModelInputMapper:
        return self._model_input_mapper

    @property
    @override
    def model_output_mapper(self) -> ModelOutputMapper:
        return self._model_output_mapper

    @property
    @override
    def model_client(self) -> Gr00tModelClient:
        return self._model_client

    def __init__(self, model_client: Gr00tModelClient,
                 model_input_mapper: ModelInputMapper,
                 model_output_mapper: ModelOutputMapper,
                 observation_handler: Sequence[ObservationHandler]) -> None:
        super().__init__(observation_handler)
        self._model_input_mapper = model_input_mapper
        self._model_output_mapper = model_output_mapper
        self._model_client = model_client

    @override
    def get_action(self, prompt: str) -> Sequence[RobotAction]:
        raw_observation = self.get_concat_observation()
        model_observation = self.model_input_mapper.transform_observation(raw_observation)
        action = self.model_client.get_action(model_observation, prompt)
        return self.model_output_mapper.to_action(action)
