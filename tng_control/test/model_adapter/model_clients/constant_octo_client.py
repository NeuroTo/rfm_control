from typing import Any
from tng_control.rfm_control.model_adapter.model_clients.model_client import ModelClient


class ConstantOctoClient(ModelClient):
    constant_action = [[[0, 0, -0.1, 0, 0, 0, 0.2],
                        [0, 0, -0.1, 0, 0, 0, 0.2],
                        [0.1, -0.1, -0.1, 0, 0, 0, 0.2],
                        [0.1, -0.1, -0.1, 0, 0, 0, 0.2]]]

    def get_action(self, observation: dict[str, Any],
                   prompt: str) -> list[list[list[float]]]:

        return self.constant_action
