from abc import ABC
import numpy as np

from tng_control.rfm_control.model_adapter.model_clients.model_client import ModelClient


Gr00tAction = dict[str, np.ndarray]


class Gr00tModelClient(ModelClient[Gr00tAction], ABC):
    """
    Interface for GR00T-specific model clients.
    All GR00T clients (real and test/mock implementations) should implement this interface.
    GR00T models return actions as dictionaries with numpy arrays (Gr00tAction).
    """
    pass

