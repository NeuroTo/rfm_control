from collections.abc import Sequence
from attr import dataclass

from tng_control.action_executor.gripper_action_executor import GripperActionExecutor
from tng_control.action_executor.joint_trajectory_action_executor import JointTrajectoryActionExecutor
from tng_control.action_executor.arm_action_executor import MotionExecutor
from tng_control.rfm_control.action_adapter.mapper.absolute_joint_action_mapper import AbsoluteJointActionMapper
from tng_control.rfm_control.action_adapter.mapper.action_mapper import ActionMapper
from tng_control.rfm_control.config.model_configs.robot_config import RobotConfig
from tng_control.rfm_control.action_adapter.mapper.delta_endeffector_action_mapper import DeltaEndeffectorActionMapper
from tng_control.rfm_control.domain_model.robot_action import RobotAction


@dataclass
class Robot():
    action_mapper: ActionMapper
    arm_action_executor: MotionExecutor
    gripper_action_executor: GripperActionExecutor
    robot_config: RobotConfig

    _current_actions: dict[int, RobotAction] = {}

    def set_actions(self, actions: Sequence[RobotAction]) -> None:
        self._current_actions = {
            action.timestep_id: action for action in actions
            if action.robot_prefix == self.robot_config.prefix}

    def get_action(self, timestep: int) -> RobotAction | None:
        if timestep in self._current_actions:
            return self._current_actions[timestep]
        return None

    @classmethod
    def from_robot_config(
            cls, robot_config: RobotConfig, action_mapper: ActionMapper | None = None):
        if action_mapper is None:
            action_mapper = AbsoluteJointActionMapper(robot_config.arm_keys.joint_names)
        arm_action_executor = JointTrajectoryActionExecutor(robot_config.arm_keys.topic_name)
        gripper_executor = GripperActionExecutor(robot_config.gripper_keys.topic_name)
        return cls(action_mapper=action_mapper,
                   arm_action_executor=arm_action_executor,
                   gripper_action_executor=gripper_executor,
                   robot_config=robot_config)

    @classmethod
    def from_robot_config_delta_action(cls, robot_config: RobotConfig):
        return Robot.from_robot_config(robot_config, DeltaEndeffectorActionMapper(robot_config))

