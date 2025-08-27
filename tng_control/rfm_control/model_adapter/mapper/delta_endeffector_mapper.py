from collections.abc import Sequence

from tng_control.rfm_control.model_adapter.mapper.model_output_mapper import ModelOutputMapper
from tng_control.domain_model.delta_endeffector_action import DeltaEndeffectorAction
from tng_control.domain_model.robot_action import RobotAction
from tng_control.domain_model.synchronous_gripper_action import SynchronousGripperAction
from tng_control.config.model_configs.robot_config import RobotConfig


class Gr00tDeltaEndeffectorMapper(ModelOutputMapper):

    def __init__(self, robot_configs: Sequence[RobotConfig]):
        self.robots = robot_configs

    def to_action(self, model_output) -> Sequence[RobotAction]:
        return [RobotAction(
            robot_config.prefix,
            i,
            DeltaEndeffectorAction(robot_action[:3], robot_action[3:6]),
            SynchronousGripperAction(gripper)
        )
            for robot_config in self.robots
            for i, (robot_action, gripper) in enumerate(zip(model_output[robot_config.arm_keys.output_position_key],
                                                            model_output[robot_config.gripper_keys.output_position_key]))]


class OctoDeltaEndeffectorMapper(ModelOutputMapper):

    def __init__(self, robot_configs: Sequence[RobotConfig]):
        self.robot = robot_configs[0]

    def to_action(self, model_output) -> Sequence[RobotAction]:
        return [RobotAction(
            self.robot.prefix,
            i,
            DeltaEndeffectorAction(
                model_output[0][i][:3],
                model_output[0][i][3:6]),
            SynchronousGripperAction(self._parse_gripper(model_output[0][i][6]))
        )
            for i in range(len(model_output[0]))]

    def _parse_gripper(self, gripper_value: float) -> float:
        return 0.001 if gripper_value > 0.5 else 0.038
