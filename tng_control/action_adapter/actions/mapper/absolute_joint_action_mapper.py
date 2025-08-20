import numpy as np

from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectoryPoint

from geometry_msgs.msg import PoseStamped
from moveit_msgs.msg import RobotState

from tng_octo.fk_solver import MoveitFKSolver
from tng_control.action_adapter.actions.mapper.action_mapper import ActionMapper
from tng_control.action_adapter.actions.mapper.pose_util import to_euler_from_quaterntion, orientation_to_list
from tng_control.action_adapter.actions.absolute_joint_state_action import AbsoluteJointStateAction
from tng_control.action_adapter.actions.robot_action import RobotAction
from tng_control.action_adapter.actions.mapper.pose_util import substract_pose


class AbsoluteJointActionMapper(ActionMapper):
    _fk_solver: MoveitFKSolver | None = None

    def __init__(self, joint_names: list[str], fk_solver=None):
        self.joint_names = joint_names
        self._fk_solver = fk_solver

    def action_to_joint_trajectory_point(
            self, action: RobotAction, state: JointState) -> JointTrajectoryPoint:
        if not isinstance(action, AbsoluteJointStateAction):
            raise ValueError("Action must be an instance of AbsoluteJointStateAction")
        point = JointTrajectoryPoint()
        point.positions = [float(x) for x in action.joint_states]
        return point

    def action_to_delta(
            self, action: RobotAction, state: JointState) -> np.ndarray | None:
        if not isinstance(action, AbsoluteJointStateAction):
            raise ValueError("Action must be an instance of AbsoluteJointStateAction")
        if self._fk_solver is None:
            raise AttributeError("FKSolver missing.")
        current_robot_state: RobotState = RobotState()
        current_robot_state.joint_state = state
        fk_output: list[PoseStamped] | None = self._fk_solver.get_pose(current_robot_state)
        if fk_output is None:
            return None
        current_pose: PoseStamped = fk_output[0]
        next_robot_state: RobotState = RobotState()
        next_robot_state.joint_state = action.joint_states
        fk_output: list[PoseStamped] | None = self._fk_solver.get_pose(next_robot_state)
        if fk_output is None:
            return None
        new_pose: PoseStamped = fk_output[0]

        position_delta = substract_pose(new_pose.pose, current_pose.pose).position
        orientation_delta = to_euler_from_quaterntion(orientation_to_list(
            new_pose.pose.orientation)) - to_euler_from_quaterntion(orientation_to_list(
                current_pose.pose.orientation))

        position_delta_list = [position_delta.x, position_delta.y, position_delta.z]
        return np.concatenate([position_delta_list, orientation_delta])
