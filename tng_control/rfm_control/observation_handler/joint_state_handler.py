from collections.abc import Sequence
from typing import Any
import math
import numpy as np
from sensor_msgs.msg import JointState as RosJointState
from rclpy.node import Node
from rclpy.subscription import Subscription
from typing_extensions import override

from tng_control.rfm_control.exceptions import JointStatesNotAvailableException
from tng_control.rfm_control.config.model_configs.robot_config import RobotConfig, RobotOutputKeys
from tng_control.rfm_control.observation_handler.observation_handler import ObservationHandler
from tng_control.rfm_control.observation_handler.observation_dto import JointState, RobotState, Observations


class JointStateHandler(ObservationHandler):

    joint_state_subscriber: Subscription | None = None

    def __init__(self, robots: Sequence[RobotConfig]) -> None:
        self.robots = robots
        self._current_joint_state: RosJointState | None = None
        self._joint_name_to_index_dict: dict[str, int] = {}
        
        # Get joint_state_topic from first robot and validate all robots use the same topic
        if not robots:
            raise ValueError("At least one robot config must be provided")
        
        self.joint_state_topic = robots[0].joint_state_topic
        
        # Validate all robots use the same joint_state_topic
        # TODO: implement real multi-joint state topic support for different joint state topics of different robots analogously to the image handler.
        for robot in robots:
            if robot.joint_state_topic != self.joint_state_topic:
                raise ValueError(
                    f"All robots must use the same joint_state_topic. "
                    f"Found {robot.prefix} with {robot.joint_state_topic}, "
                    f"expected {self.joint_state_topic}"
                )

    @override
    def create_subscription(self, node: Node) -> None:
        if self.joint_state_subscriber is not None:
            return
        self.joint_state_subscriber = node.create_subscription(
            RosJointState,
            self.joint_state_topic,
            self._update_callback,
            10)

    @override
    def get_observations(self) -> Observations:
        """
        Get robot joint state observations.
        
        Returns a partial Observations object with robot data populated.
        Images field uses default (empty dict).
        """
        robots_data = []
        
        for robot in self.robots:
            arm_data = self._get_joint_state(robot.arm_keys)
            gripper_data = self._get_joint_state(robot.gripper_keys)
            
            robots_data.append(RobotState(
                prefix=robot.prefix,
                arm=arm_data,
                gripper=gripper_data
            ))
        
        return Observations(robots=robots_data)

    def get_current_joint_state(self) -> RosJointState:
        """Get the current ROS2 joint state message."""
        if not self._current_joint_state:
            raise JointStatesNotAvailableException()
        return self._current_joint_state

    def _get_joint_data(self, joint_name: str) -> tuple[float, float, float]:
        idx = self._joint_name_to_index(joint_name)
        joint_state = self.get_current_joint_state()
        # Return raw values in radians (no model-specific transformation)
        return (
            joint_state.position[idx],
            joint_state.velocity[idx],
            joint_state.effort[idx]
        )

    def _joint_name_to_index(self, joint_name: str) -> int:
        if not self._joint_name_to_index_dict:
            self._joint_name_to_index_dict = {name: i for i,
                                              name in enumerate(self.get_current_joint_state().name)}
        return self._joint_name_to_index_dict[joint_name]

    def _update_callback(self, joint_state: RosJointState) -> None:
        self._current_joint_state = joint_state

    def _get_joint_state(self, robot_keys: RobotOutputKeys) -> JointState:
        """
        Get joint state for a set of joints.
        
        Returns raw joint data in radians without model-specific transformations.
        """
        joint_name_array = robot_keys.joint_names
        joint_positions, joint_velocities, joint_efforts = ([], [], [])

        # Extract data for each joint
        for joint_name in joint_name_array:
            pos, vel, effort = self._get_joint_data(joint_name)
            joint_positions.append(pos)
            joint_velocities.append(vel)
            joint_efforts.append(effort)

        return JointState(
            positions=np.array(joint_positions),
            velocities=np.array(joint_velocities),
            efforts=self._remove_nan_entries(joint_efforts),
            joint_names=joint_name_array
        )

    def _remove_nan_entries(self, values_in_radians):
        return np.array(
            [[0 if math.isnan(value) else value for value in values_in_radians]])

