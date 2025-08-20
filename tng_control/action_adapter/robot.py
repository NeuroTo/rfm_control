from collections.abc import Sequence
from attr import dataclass

from tng_control.action_adapter.action_executor.gripper_action_executor import GripperActionExecutor
from tng_control.action_adapter.action_executor.trajectory_action_executor import TrajectoryActionExecutor
from tng_control.action_adapter.action_executor.robot_action_executor import RobotActionExecutor
from tng_control.action_adapter.actions.mapper.absolute_joint_action_mapper import AbsoluteJointActionMapper
from tng_control.action_adapter.actions.mapper.action_mapper import ActionMapper
from tng_control.config.model_configs.robot_config import RobotConfig
from tng_control.action_adapter.actions.mapper.delta_endeffector_action_mapper import DeltaEndeffectorActionMapper
from tng_control.action_adapter.actions.action import Action


@dataclass
class Robot():
    action_mapper: ActionMapper
    robot_action_executor: RobotActionExecutor
    gripper_action_executor: GripperActionExecutor
    robot_config: RobotConfig

    _current_actions: dict[int, Action] = {}

    def set_actions(self, actions: Sequence[Action]) -> None:
        self._current_actions = {
            action.timestep_id: action for action in actions
            if action.robot_prefix == self.robot_config.prefix}

    def get_action(self, timestep: int) -> Action | None:
        if timestep in self._current_actions:
            return self._current_actions[timestep]
        return None

    @classmethod
    def from_robot_config(
            cls, robot_config: RobotConfig, action_mapper: ActionMapper | None = None):
        if action_mapper is None:
            action_mapper = AbsoluteJointActionMapper(robot_config.arm_keys.joint_names)
        robot_action_executor = TrajectoryActionExecutor(
            robot_config.arm_keys.topic_name, robot_config.arm_keys.joint_names)
        gripper_executor = GripperActionExecutor(robot_config.gripper_keys.topic_name)
        return cls(action_mapper=action_mapper,
                   robot_action_executor=robot_action_executor,
                   gripper_action_executor=gripper_executor,
                   robot_config=robot_config)

    @classmethod
    def from_robot_config_delta_action(cls, robot_config: RobotConfig):
        return Robot.from_robot_config(robot_config, DeltaEndeffectorActionMapper(robot_config))
