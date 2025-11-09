from abc import ABC

from tng_control.rfm_control.model_adapter.model_clients.model_client import ModelClient


OctoAction = list[list[list[float]]]


class OctoModelClient(ModelClient[OctoAction], ABC):
    """
    Interface for Octo-specific model clients.
    All Octo clients (real and test/mock implementations) should implement this interface.
    Octo models return actions as nested lists of floats (OctoAction).
    """
    pass

