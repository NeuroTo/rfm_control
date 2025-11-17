from abc import ABC, abstractmethod
import numpy as np

from tng_control.rfm_control.observation_handler.observation_dto import Observations


class ModelInputMapper(ABC):
    """
    Transforms generic observations to model-specific input format.
    
    This provides symmetry with ModelOutputMapper - while the output mapper
    transforms model outputs to robot actions, the input mapper transforms
    generic observations to model-specific input format.
    
    Responsibilities:
        - Map generic observation structure to model-specific keys
        - Apply model-specific transformations (e.g., scaling, normalization)
        - Add model-specific metadata (e.g., timestep_pad_mask for Octo)
        - Resize and transform images to model-specific format
    
    The input is a type-safe GenericObservations dataclass:
        GenericObservations(
            robots=[RobotObservation(prefix=str, arm=JointArrayData(...), ...)],
            images={topic_name: np.ndarray}
        )
    
    The output is model-specific, e.g. for GR00T:
        {
            "state.joint_positions": np.ndarray,
            "state.gripper": np.ndarray,
            "video.wrist": np.ndarray,
            ...
        }
    """
    
    @abstractmethod
    def transform_observation(self, observations: Observations) -> dict[str, np.ndarray]:
        """
        Transform generic observations to model-specific format.
        
        Args:
            observations: Type-safe Observations from ModelPort
            
        Returns:
            Model-specific observation dict ready for inference
        """
        pass

