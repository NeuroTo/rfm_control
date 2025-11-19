from typing import Any
import os
import jax
from typing_extensions import override

from octo.model.octo_model import OctoModel

from rfm_control.config.model_client_config_base import OctoConfigBase
from rfm_control.model_adapter.model_clients.octo.octo_model_client import OctoModelClient, OctoAction


class OctoClient(OctoModelClient):

    def __init__(self, config: OctoConfigBase):
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        self.model = OctoModel.load_pretrained(config.model_path)
        self.statistics = config.get_dataset_statistics(self.model)
        self.random_key = jax.random.PRNGKey(0)

    @override
    def get_action(self, observation: dict[str, Any],
                   prompt: str) -> OctoAction:

        return self.model.sample_actions(
            observation,
            self.create_task(prompt),
            unnormalization_statistics=self.statistics,
            rng=self.random_key
        )

    def create_task(self, prompt: str) -> dict[str, dict]:
        return self.model.create_tasks(texts=[prompt])
