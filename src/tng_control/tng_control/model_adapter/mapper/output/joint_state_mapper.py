from collections.abc import Sequence
import numpy as np
from typing_extensions import override

from tng_control.domain_model.robot_action import RobotAction
from tng_control.domain_model.synchronous_gripper_action import SynchronousGripperAction
from tng_control.domain_model.absolute_joint_state_action import AbsoluteJointStateAction
from tng_control.model_adapter.mapper.output.model_output_mapper import ModelOutputMapper
from tng_control.config.config_models.robot_config import RobotConfig
from tng_control.model_adapter.model_clients.gr00t.gr00t_model_client import Gr00tAction


class Gr00tJointStateMapper(ModelOutputMapper[Gr00tAction]):

    def __init__(self, robots_configs: Sequence[RobotConfig]):
        self.robots = robots_configs

    @override
    def to_action(self, model_output: Gr00tAction) -> Sequence[RobotAction]:
        actions: list[RobotAction] = []
        for robot_config in self.robots:
            for i, (joint_positions, gripper_aperture) in enumerate(zip(
                model_output[robot_config.arm_config.model_output_position_key],
                model_output[robot_config.gripper_config.model_output_position_key])):
                actions.append(self._to_robot_action(robot_config, i, joint_positions, gripper_aperture))
        return actions

    def _to_robot_action(self, robot_config: RobotConfig, timestep: int, joint_positions: np.ndarray, gripper_aperture: float) -> RobotAction:
        # transform from policy model scale to real joint angles
        joint_states = np.array(joint_positions) * np.pi / 100
        gripper_aperture = float(gripper_aperture) * np.pi / 100

        return RobotAction(
            robot_prefix=robot_config.prefix,
            timestep_id=timestep,
            arm_action=AbsoluteJointStateAction(joint_states=joint_states,
                                                time_between_goals=robot_config.time_between_goals),
            gripper_action=SynchronousGripperAction(gripper_aperture=gripper_aperture)
        )

class Gr00tJointStateMapperRTC(ModelOutputMapper[Gr00tAction]):

    def __init__(self, robots_configs: Sequence[RobotConfig]):
        self.robots = robots_configs

    # TODO: check if Gr00tJointStateMapper is not sufficient for RTC.
    #  Shouldn't the model_output simply contain only one element but could still run through the loop of the Gr00tJointStateMapper implementation?
    @override
    def to_action(self, model_output: Gr00tAction) -> Sequence[RobotAction]:
        actions: list[RobotAction] = []
        for robot_config in self.robots:
            actions.append(self._to_robot_action(robot_config, model_output))
        return actions

    def _to_robot_action(self, robot_config: RobotConfig, model_action: Gr00tAction) -> RobotAction:
        joint_states = np.array(model_action[robot_config.arm_config.model_output_position_key]) * np.pi / 100
        gripper_aperture = float(model_action[robot_config.gripper_config.model_output_position_key]) * np.pi / 100

        return RobotAction(
            robot_prefix=robot_config.prefix,
            timestep_id=0,
            arm_action=AbsoluteJointStateAction(joint_states=joint_states,
                                                time_between_goals=robot_config.time_between_goals),
            gripper_action=SynchronousGripperAction(gripper_aperture=gripper_aperture)
        )

