from abc import ABC, abstractmethod
import numpy as np
from rclpy.node import Node


class ObservationHandler(ABC):
    @abstractmethod
    def get_observation_dict(self) -> dict[str, np.ndarray]:
        pass

    @abstractmethod
    def create_subscription(self, node: Node) -> None:
        pass

