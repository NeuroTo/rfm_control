from typing import Any
from typing_extensions import override

from tng_control.rfm_control.model_adapter.model_clients.octo.octo_model_client import OctoModelClient, OctoAction


class OctoClientMock(OctoModelClient):
    """Mock client implementation for Octo model testing."""
    
    constant_action = [[[0, 0, -0.1, 0, 0, 0, 0.2],
                        [0, 0, -0.1, 0, 0, 0, 0.2],
                        [0.1, -0.1, -0.1, 0, 0, 0, 0.2],
                        [0.1, -0.1, -0.1, 0, 0, 0, 0.2]]]

    @override
    def get_action(self, observation: dict[str, Any],
                   prompt: str) -> OctoAction:

        return self.constant_action

