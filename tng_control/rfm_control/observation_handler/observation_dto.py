"""Generic observation DTOs (Data Transfer Objects)."""
from dataclasses import dataclass, field
import numpy as np


@dataclass
class JointState:
    """
    Joint state data (for arm or gripper).
    
    All values in radians without model-specific transformations.
    """
    positions: np.ndarray
    velocities: np.ndarray
    efforts: np.ndarray
    joint_names: list[str]


@dataclass
class RobotState:
    """
    Joint state for one robot.
    
    Contains arm and gripper data with robot prefix for identification.
    """
    prefix: str
    arm: JointState
    gripper: JointState


@dataclass
class Observations:
    """
    Complete generic observation structure.
    
    This is the output format from ObservationHandlers.
    
    Fields have sensible defaults so handlers can provide partial observations.
    """
    robots: list[RobotState] = field(default_factory=list)
    images: dict[str, np.ndarray] = field(default_factory=dict)  # topic_name -> raw image (not resized)

