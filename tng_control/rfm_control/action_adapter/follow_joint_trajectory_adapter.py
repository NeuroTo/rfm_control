from collections.abc import Sequence
from typing_extensions import override
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint
from control_msgs.msg import GripperCommand as GripperCommandMessage
from builtin_interfaces.msg import Duration

from tng_control.rfm_control.domain_model.robot_action import RobotAction
from tng_control.rfm_control.action_adapter.action_port import ActionPort
from tng_control.rfm_control.status_code import RfmControlStatusCode
from tng_control.rfm_control.action_adapter.joint_state_subscriber import JointStateSubscriber
from tng_control.rfm_control.action_adapter.robot import Robot


class FollowJointTrajectoryAdapter(ActionPort):

    @property
    @override
    def robots(self) -> Sequence[Robot]:
        return self._robots

    @robots.setter
    def robots(self, value: Sequence[Robot]):
        self._robots = value

    @property
    @override
    def joint_state_subscriber(self) -> JointStateSubscriber:
        return self._joint_state_subscriber

    @joint_state_subscriber.setter
    def joint_state_subscriber(self, value: JointStateSubscriber):
        self._joint_state_subscriber = value

    def __init__(
            self, robots: Sequence[Robot],
            joint_state_subscriber: JointStateSubscriber):
        self.robots = robots
        self.joint_state_subscriber = joint_state_subscriber

    @override
    def move(self, node: Node, actions: Sequence[RobotAction], action_execution_horizon: int) -> RfmControlStatusCode:

        for robot in self.robots:
            robot.set_actions(actions)

        for t in range(action_execution_horizon):
            futures = []
            for robot in self.robots:
                action = robot.get_action(t)
                if action is None:
                    continue

                trajectory_point = robot.action_mapper.action_to_joint_trajectory_point(
                    action.arm_action, self.joint_state_subscriber.get_current_joint_state())

                if trajectory_point is None:
                    return RfmControlStatusCode.ACTION_MAPPING_FAILED
                self._add_timestamps_to_trajectory(trajectory_point, action.arm_action.time_between_goals)
                gripper_action = action.gripper_action

                robot_action_future = robot.arm_action_executor.execute_async(
                    [trajectory_point], node)
                gripper_action_future = robot.gripper_action_executor.execute_async(
                    GripperCommandMessage(position=gripper_action.gripper_aperture, max_effort=2.0),
                    node)

                futures.append(robot_action_future)
                futures.append(gripper_action_future)

            for future in futures:
                rclpy.spin_until_future_complete(node, future)

        return RfmControlStatusCode.SUCCESS

    def _add_timestamps_to_trajectory(
            self, trajectory_point: JointTrajectoryPoint, time_between_goals: float) -> None:
        duration_between_goals = Duration(
            sec=int(time_between_goals),
            nanosec=int((time_between_goals % 1) * 1e9))

        trajectory_point.time_from_start = duration_between_goals
