from collections.abc import Sequence
from typing_extensions import override

import rclpy
from rclpy.node import Node
from control_msgs.msg import GripperCommand as GripperCommandMessage
from trajectory_msgs.msg import JointTrajectory

from tng_control.domain_model.robot_action import RobotAction
from tng_control.domain_model.synchronous_gripper_action import SynchronousGripperAction
from tng_control.action_adapter.action_port import ActionPort
from tng_control.status_code import RfmControlStatusCode
from tng_control.observation_handler.joint_state_handler import JointStateHandler
from tng_control.action_adapter.robot import Robot


class FollowJointTrajectoryAdapter(ActionPort):
    """
    Action adapter for robots using FollowJointTrajectory controller.
    
    Maps actions to JointTrajectory messages and executes them on the robot
    """

    @property
    @override
    def robots(self) -> Sequence[Robot[JointTrajectory]]:
        return self._robots

    @robots.setter
    def robots(self, value: Sequence[Robot[JointTrajectory]]):
        self._robots = value

    @property
    @override
    def joint_state_handler(self) -> JointStateHandler:
        return self._joint_state_handler

    @joint_state_handler.setter
    def joint_state_handler(self, value: JointStateHandler):
        self._joint_state_handler = value

    def __init__(
            self, robots: Sequence[Robot[JointTrajectory]],
            joint_state_handler: JointStateHandler):
        self.robots = robots
        self.joint_state_handler = joint_state_handler

    @override
    def move(self, node: Node, actions: Sequence[RobotAction], action_execution_horizon: int) -> RfmControlStatusCode:

        # Route actions to the correct robots based on robot_prefix
        for robot in self.robots:
            robot_actions = [action for action in actions if action.robot_prefix == robot.prefix]
            robot.set_actions(robot_actions)

        for t in range(action_execution_horizon):
            futures = []
            for robot in self.robots:
                action = robot.get_action(t)
                if action is None:
                    continue

                try:
                    trajectory: JointTrajectory = robot.action_mapper.map_action_to_executor_input(
                        action.arm_action, 
                        self.joint_state_handler.get_current_joint_state()
                    )
                except (ValueError, RuntimeError) as e:
                    # Action mapping failed (e.g., IK failed, invalid action type)
                    node.get_logger().error(f"Action mapping failed for robot {robot.prefix}: {e}")
                    return RfmControlStatusCode.ACTION_MAPPING_FAILED

                robot_action_future = robot.arm_action_executor.execute_async(trajectory, node)
                
                # Handle gripper action (currently only supports SynchronousGripperAction)
                gripper_action = action.gripper_action
                if isinstance(gripper_action, SynchronousGripperAction):
                    gripper_action_future = robot.gripper_action_executor.execute_async(
                        GripperCommandMessage(position=gripper_action.gripper_aperture, max_effort=2.0),
                        node)
                    futures.append(gripper_action_future)
                else:
                    node.get_logger().warn(f"Unsupported gripper action type: {type(gripper_action)}")

                futures.append(robot_action_future)

            # Wait for all actions in this timestep to complete
            for future in futures:
                rclpy.spin_until_future_complete(node, future)

        return RfmControlStatusCode.SUCCESS
