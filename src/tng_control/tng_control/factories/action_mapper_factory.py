"""Factory for creating action mappers."""
from typing import Callable

from trajectory_msgs.msg import JointTrajectory

from tng_control.config.config_types import ACTION_MAPPER_TYPE_ABSOLUTE_JOINT, ACTION_MAPPER_TYPE_DELTA_ENDEFFECTOR
from tng_control.action_adapter.mapper.action_mapper import ActionMapper
from tng_control.action_adapter.mapper.absolute_joint_action_mapper import AbsoluteJointActionMapper
from tng_control.action_adapter.mapper.delta_endeffector_action_mapper import DeltaEndeffectorActionMapper
from tng_control.config.config_models.robot_config import RobotConfig


class ActionMapperFactory:
    """
    Factory for creating action mappers.
    
    Creates ActionMapper instances based on type string.
    Factory methods are self-contained (no external dependencies).
    """
    
    def __init__(self):
        self._registry: dict[str, Callable[[RobotConfig], ActionMapper[JointTrajectory]]] = {
            ACTION_MAPPER_TYPE_ABSOLUTE_JOINT: self._create_absolute_joint_to_joint_trajectory_mapper,
            ACTION_MAPPER_TYPE_DELTA_ENDEFFECTOR: self._create_delta_endeffector_to_joint_trajectory_mapper,
        }
    
    def create(self, mapper_type: str, robot_config: RobotConfig) -> ActionMapper[JointTrajectory]:
        """
        Create action mapper based on type.
        
        Args:
            mapper_type: Type of action mapper ('absolute_joint', 'delta_endeffector')
            robot_config: Robot configuration
            
        Returns:
            ActionMapper instance
            
        Raises:
            ValueError: If mapper_type is not registered
        """
        factory_method = self._registry.get(mapper_type)
        
        if factory_method is None:
            raise ValueError(
                f"Unknown action mapper type: '{mapper_type}'. "
                f"Supported types: {list(self._registry.keys())}"
            )
        
        return factory_method(robot_config)
    
    def _create_absolute_joint_to_joint_trajectory_mapper(self, robot_config: RobotConfig) -> ActionMapper[JointTrajectory]:
        """Create absolute joint action mapper."""
        return AbsoluteJointActionMapper(robot_config.arm_config.joint_names)
    
    def _create_delta_endeffector_to_joint_trajectory_mapper(self, robot_config: RobotConfig) -> ActionMapper[JointTrajectory]:
        """Create delta endeffector action mapper."""
        return DeltaEndeffectorActionMapper(robot_config)
    
    @property
    def supported_types(self) -> list[str]:
        """Get list of supported action mapper types."""
        return list(self._registry.keys())


