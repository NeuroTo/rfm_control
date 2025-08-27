from typing import Any
import os
import jax

from octo.model.octo_model import OctoModel

from tng_control.config.model_configs.octo_config import OctoConfig
from tng_control.rfm_control.model_adapter.model_clients.model_client import ModelClient


class OctoClient(ModelClient):

    def __init__(self, config: OctoConfig):
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        self.model = OctoModel.load_pretrained(config.model_path)
        self.statistics = config.get_dataset_statistics(self.model)
        self.random_key = jax.random.PRNGKey(0)

    def get_action(self, observation: dict[str, Any],
                   prompt: str) -> list[list[list[float]]]:

        return self.model.sample_actions(
            observation,
            self.create_task(prompt),
            unnormalization_statistics=self.statistics,
            rng=self.random_key
        )

    def create_task(self, prompt: str) -> dict[str, dict]:
        return self.model.create_tasks(texts=[prompt])
