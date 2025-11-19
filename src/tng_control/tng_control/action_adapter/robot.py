from collections.abc import Sequence
from typing import Generic, TypeVar

from tng_control.action_executor.gripper_action_executor import GripperActionExecutor
from tng_control.action_executor.motion_executor import MotionExecutor
from tng_control.action_adapter.mapper.action_mapper import ActionMapper
from tng_control.domain_model.robot_action import RobotAction


CommandType = TypeVar('CommandType')


class Robot(Generic[CommandType]):
    """
    Robot instance that coordinates action mapping and execution.
    
    Type parameter CommandType defines the command format used by the action mapper
    and executor (e.g., JointTrajectory for FollowJointTrajectory action).
    """

    def __init__(
        self,
        prefix: str,
        action_mapper: ActionMapper[CommandType],
        arm_action_executor: MotionExecutor[CommandType],
        gripper_action_executor: GripperActionExecutor
    ) -> None:
        """
        Initialize a Robot instance.
        
        Args:
            prefix: Robot identifier prefix for action routing and logging
            action_mapper: Action mapper to convert model actions to executor commands
            arm_action_executor: Executor for arm motion commands
            gripper_action_executor: Executor for gripper commands
        """
        self.prefix = prefix
        self.action_mapper = action_mapper
        self.arm_action_executor = arm_action_executor
        self.gripper_action_executor = gripper_action_executor
        self._current_actions: dict[int, RobotAction] = {}

    def set_actions(self, actions: Sequence[RobotAction]) -> None:
        """Store actions indexed by timestep."""
        self._current_actions = {action.timestep_id: action for action in actions}

    def get_action(self, timestep: int) -> RobotAction | None:
        if timestep in self._current_actions:
            return self._current_actions[timestep]
        return None
