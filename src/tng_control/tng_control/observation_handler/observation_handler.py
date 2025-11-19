from abc import ABC, abstractmethod
from rclpy.node import Node

from tng_control.observation_handler.observation_dto import Observations


class ObservationHandler(ABC):
    """
    Generic observation handler that collects robot sensor data.
    
    Returns model-agnostic observation data. The transformation
    to model-specific format is handled by ModelInputMapper.
    
    Each handler returns a partial Observations object:
    - JointStateHandler: Observations with populated robots, empty images
    - ImageHandler: Observations with populated images, empty robots
    
    ModelPort merges these partial observations into a complete Observations object.
    """
    
    @abstractmethod
    def get_observations(self) -> Observations:
        """
        Get observations from this handler.
        
        Returns a partial Observations object. Handlers populate only their
        relevant fields and leave others empty.
        """
        pass

    @abstractmethod
    def create_subscription(self, node: Node) -> None:
        pass

