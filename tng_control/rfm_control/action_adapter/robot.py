from trajectory_msgs.msg._joint_trajectory import JointTrajectory


from collections.abc import Sequence
from typing import Generic
from attr import dataclass

from trajectory_msgs.msg import JointTrajectory

from tng_control.action_executor.gripper_action_executor import GripperActionExecutor
from tng_control.action_executor.joint_trajectory_action_executor import JointTrajectoryActionExecutor
from tng_control.action_executor.motion_executor import MotionExecutor, CommandType
from tng_control.rfm_control.action_adapter.mapper.absolute_joint_action_mapper import AbsoluteJointActionMapper
from tng_control.rfm_control.action_adapter.mapper.action_mapper import ActionMapper
from tng_control.rfm_control.config.model_configs.robot_config import RobotConfig
from tng_control.rfm_control.action_adapter.mapper.delta_endeffector_action_mapper import DeltaEndeffectorActionMapper
from tng_control.rfm_control.domain_model.robot_action import RobotAction


@dataclass
class Robot(Generic[CommandType]):
    """
    Robot instance that coordinates action mapping and execution.
    
    Type parameter CommandType matches the command type used by the action_mapper
    and the arm_action_executor (e.g., JointTrajectory for FollowJointTrajectory controller).
    """
    action_mapper: ActionMapper[CommandType]
    # TODO: try to handle arm_action_executor and gripper_action_executor in a more generic way.
    arm_action_executor: MotionExecutor[CommandType]
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
    def from_robot_config(cls, robot_config: RobotConfig) -> 'Robot[JointTrajectory]':
        """Create Robot with absolute joint action mapper."""
        action_mapper: ActionMapper[JointTrajectory] = AbsoluteJointActionMapper(robot_config.arm_keys.joint_names)
        arm_action_executor: MotionExecutor[JointTrajectory] = JointTrajectoryActionExecutor(robot_config.arm_keys.topic_name)
        gripper_executor = GripperActionExecutor(robot_config.gripper_keys.topic_name)
        return Robot[JointTrajectory](action_mapper=action_mapper,
                   arm_action_executor=arm_action_executor,
                   gripper_action_executor=gripper_executor,
                   robot_config=robot_config)

    @classmethod
    def from_robot_config_delta_action(cls, robot_config: RobotConfig) -> 'Robot[JointTrajectory]':
        """Create Robot with delta endeffector action mapper."""
        action_mapper: ActionMapper[JointTrajectory] = DeltaEndeffectorActionMapper(robot_config)
        arm_action_executor: MotionExecutor[JointTrajectory] = JointTrajectoryActionExecutor(robot_config.arm_keys.topic_name)
        gripper_executor = GripperActionExecutor(robot_config.gripper_keys.topic_name)
        return Robot[JointTrajectory](action_mapper=action_mapper,
                   arm_action_executor=arm_action_executor,
                   gripper_action_executor=gripper_executor,
                   robot_config=robot_config)
