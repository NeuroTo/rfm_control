from collections.abc import Sequence
from typing_extensions import override
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectoryPoint
from control_msgs.msg import GripperCommand
from builtin_interfaces.msg import Duration

from tng_control.domain_model.robot_action import RobotAction
from tng_control.action_adapter.action_port import ActionPort
from tng_control.rfm_control.status_code import RfmControlStatusCode
from tng_control.config.model_configs.model_config import ModelConfig
from tng_control.rfm_control.model_adapter.observation_handler.joint_state_handler import JointStateHandler
from tng_control.action_adapter.robot import Robot


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
    def joint_state_handler(self) -> JointStateHandler:
        return self._joint_state_handler

    @joint_state_handler.setter
    def joint_state_handler(self, value: JointStateHandler):
        self._joint_state_handler = value

    def __init__(
            self, robots: Sequence[Robot],
            config: ModelConfig, joint_state_handler: JointStateHandler):
        self.robots = robots
        self.config = config
        self.joint_state_handler = joint_state_handler

    @override
    def move(self, actions: Sequence[RobotAction], node: Node) -> RfmControlStatusCode:

        for robot in self.robots:
            robot.set_actions(actions)

        for i in range(self.config.action_horizon):
            futures = []
            for robot in self.robots:
                action = robot.get_action(i)
                if action is None:
                    continue

                trajectory_point = robot.action_mapper.action_to_joint_trajectory_point(
                    action.robot_action, self.joint_state_handler.get_current_joint_state())

                if trajectory_point is None:
                    return RfmControlStatusCode.ACTION_MAPPING_FAILED
                self._add_timestamps_to_trajectory(trajectory_point)
                gripper_action = action.gripper_action

                robot_action_future = robot.robot_action_executor.execute_action(
                    [trajectory_point], node)
                gripper_action_future = robot.gripper_action_executor.execute_gripper_action(
                    GripperCommand(position=gripper_action.gripper_aperture, max_effort=2.0),
                    node)

                futures.append(robot_action_future)
                futures.append(gripper_action_future)

            for future in futures:
                rclpy.spin_until_future_complete(node, future)

        return RfmControlStatusCode.SUCCESS

    def _add_timestamps_to_trajectory(
            self, trajectory_point: JointTrajectoryPoint) -> None:
        duration_between_goals = Duration(
            sec=int(self.config.time_between_goals),
            nanosec=int((self.config.time_between_goals % 1) * 1e9))

        trajectory_point.time_from_start = duration_between_goals
