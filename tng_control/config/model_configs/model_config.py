from abc import abstractmethod
from dataclasses import dataclass, field

from tng_control.rfm_control.model_adapter.observation_handler.image_feature import ImageFeature
from tng_control.config.model_configs.robot_config import RobotConfig
from tng_robot_arms_shared import Ros2ControlJointConfig


@dataclass
class ModelConfig:
    """Configuration for robot control models"""
    _ros2_control_configs: list[Ros2ControlJointConfig]
    _robot_configs: list[RobotConfig] = field(init=False)

    def __post_init__(self):
        # Validate that we have at least one robot config
        if not self.robot_configs:
            raise ValueError("At least one RobotConfig must be provided")

        for robot in self._robot_configs:
            for ros2_robot_config in self._ros2_control_configs:
                if robot.prefix == ros2_robot_config.prefix:
                    robot.arm_keys.joint_names = ros2_robot_config.arm_joints
                    robot.gripper_keys.joint_names = [ros2_robot_config.gripper_joint]

    @property
    @abstractmethod
    def robot_configs(self) -> list[RobotConfig]:
        return self._robot_configs

    @property
    @abstractmethod
    def image_features(self) -> list[ImageFeature]:
        pass

    @property
    @abstractmethod
    def frame_id(self) -> str:
        pass

    @property
    @abstractmethod
    def joint_state_topic(self) -> str:
        pass

    @property
    @abstractmethod
    def action_horizon(self) -> int:
        pass

    @property
    @abstractmethod
    def time_between_goals(self) -> float:
        pass
