from collections.abc import Sequence
from typing import cast
import numpy as np

from tng_control.domain_model.robot_action import RobotAction
from tng_control.domain_model.synchronous_gripper_action import SynchronousGripperAction
from tng_control.domain_model.absolute_joint_state_action import AbsoluteJointStateAction
from tng_control.rfm_control.model_adapter.mapper.model_output_mapper import ModelOutputMapper
from tng_control.config.model_configs.robot_config import RobotConfig


class Gr00tJointStateMapper(ModelOutputMapper):

    def __init__(self, robots_configs: Sequence[RobotConfig]):
        self.robots = robots_configs

    def to_action(self, model_output: dict[str, list[list[float] | float]]) -> Sequence[RobotAction]:
        return [RobotAction(
            robot_config.prefix,
            i,
            AbsoluteJointStateAction(np.array(robot_action) * np.pi / 100),
            SynchronousGripperAction(float(cast(float, gripper)) * np.pi / 100)
        ) for robot_config in self.robots
            for i, (robot_action, gripper) in enumerate(zip(model_output[robot_config.arm_keys.output_position_key],
                                                            model_output[robot_config.gripper_keys.output_position_key]))]


class Gr00tJointStateMapperRTC(ModelOutputMapper):

    def __init__(self, robots_configs: Sequence[RobotConfig]):
        self.robots = robots_configs

    def to_action(self, model_output: dict[str, list[list[float] | float]]) -> Sequence[RobotAction]:
        return [RobotAction(
            robot_config.prefix,
            0,
            AbsoluteJointStateAction(
                np.array(model_output[robot_config.arm_keys.output_position_key]) * np.pi / 100),
            SynchronousGripperAction(
                float(cast(float, model_output[robot_config.gripper_keys.output_position_key])) * np.pi / 100)
        ) for robot_config in self.robots]
