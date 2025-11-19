"""Factory for creating action adapters."""
from typing import Callable

from rfm_control.config.config_types import ACTION_TYPE_FOLLOW_JOINT_TRAJECTORY
from rfm_control.action_executor.gripper_action_executor import GripperActionExecutor
from rfm_control.action_executor.joint_trajectory_action_executor import JointTrajectoryActionExecutor
from rfm_control.action_adapter.action_port import ActionPort
from rfm_control.action_adapter.follow_joint_trajectory_adapter import FollowJointTrajectoryAdapter
from rfm_control.action_adapter.robot import Robot
from rfm_control.config.config_schema import RfmConfigYaml
from rfm_control.config.config_models.robot_config import RobotConfig
from rfm_control.factories.action_mapper_factory import ActionMapperFactory
from rfm_control.observation_handler.joint_state_handler import JointStateHandler
from trajectory_msgs.msg import JointTrajectory


ActionAdapterFactoryMethod = Callable[
    [list[RobotConfig], JointStateHandler, RfmConfigYaml],
    ActionPort
]


class ActionAdapterFactory:
    """
    Factory for creating action adapters.
    
    Creates ActionPort instances based on action type string.
    Requires ActionMapperFactory to create robots with appropriate mappers.
    """
    
    def __init__(self, action_mapper_factory: ActionMapperFactory | None = None):
        self.action_mapper_factory = action_mapper_factory or ActionMapperFactory()
        self._registry: dict[str, ActionAdapterFactoryMethod] = {
            ACTION_TYPE_FOLLOW_JOINT_TRAJECTORY: self._create_follow_joint_trajectory_adapter,
        }
    
    def create(
        self,
        action_type: str,
        robot_configs: list[RobotConfig],
        joint_state_handler: JointStateHandler,
        yaml_config: RfmConfigYaml
    ) -> ActionPort:
        """
        Create action adapter based on type.
        
        Args:
            action_type: Type of action adapter
            robot_configs: Robot configurations
            joint_state_handler: Joint state observation handler
            yaml_config: Complete YAML configuration
            
        Returns:
            ActionPort instance
            
        Raises:
            ValueError: If action_type is not registered
        """
        factory_method = self._registry.get(action_type)
        
        if factory_method is None:
            raise ValueError(
                f"Unknown action type: '{action_type}'. "
                f"Supported types: {list(self._registry.keys())}"
            )
        
        return factory_method(robot_configs, joint_state_handler, yaml_config)
    
    def _create_follow_joint_trajectory_adapter(self, robot_configs: list[RobotConfig], joint_state_handler: JointStateHandler, yaml_config: RfmConfigYaml) -> ActionPort:
        """Create FollowJointTrajectory action adapter with JointTrajectory robots."""
        # Get action mapper type from config
        mapper_type = yaml_config.action.arm_action_mapper
        
        # Create robots with JointTrajectory command type and appropriate action mapper
        robots = [
            Robot[JointTrajectory](
                prefix=robot.prefix,
                action_mapper=self.action_mapper_factory.create(mapper_type, robot),
                arm_action_executor=JointTrajectoryActionExecutor(robot.arm_config.topic_name),
                gripper_action_executor=GripperActionExecutor(robot.gripper_config.topic_name)
            )
            for robot in robot_configs
        ]
        
        return FollowJointTrajectoryAdapter(robots, joint_state_handler)
    
    @property
    def supported_types(self) -> list[str]:
        """Get list of supported action types."""
        return list(self._registry.keys())


