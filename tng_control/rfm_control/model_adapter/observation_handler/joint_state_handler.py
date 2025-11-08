from collections.abc import Sequence
import math
import numpy as np
from sensor_msgs.msg import JointState
from rclpy.node import Node
from rclpy.subscription import Subscription

from tng_control.rfm_control.exceptions import JointStatesNotAvailableException
from tng_control.action_adapter.robot import Robot, RobotConfig
from tng_control.rfm_control.model_adapter.observation_handler.observation_handler import ObservationHandler
from tng_control.config.model_configs.robot_config import RobotOutputKeys


class JointStateHandler(ObservationHandler):

    joint_state_subscriber: Subscription | None = None

    def __init__(self, robots: Sequence[RobotConfig], topic_name: str) -> None:
        self.joint_state_topic = topic_name
        self.robots = robots
        self._current_joint_state: JointState | None = None
        self._joint_name_to_index_dict: dict[str, int] = {}

    def create_subscription(self, node: Node) -> None:
        if self.joint_state_subscriber is not None:
            return
        self.joint_state_subscriber = node.create_subscription(
            JointState,
            self.joint_state_topic,
            self._update_callback,
            10)

    def get_observation_dict(self) -> dict[str, np.ndarray]:
        """Map current joint states to an observation dictionary format expected by the model."""
        result_dict = {}

        for robot in self.robots:
            result_dict |= self._get_observation_dict_for_joint_array(robot.arm_keys)
            result_dict |= self._get_observation_dict_for_joint_array(robot.gripper_keys)

        return result_dict

    def get_current_joint_state(self) -> JointState:
        if not self._current_joint_state:
            raise JointStatesNotAvailableException()
        return self._current_joint_state

    def get_robot_state(self, robot: Robot) -> list[float]:
        joint_state = self.get_current_joint_state()
        return [joint_state.position[self._joint_name_to_index(joint)]
                for joint in robot.robot_config.arm_keys.joint_names]

    def _get_joint_data(self, joint_name: str) -> tuple[float, float, float]:
        idx = self._joint_name_to_index(joint_name)
        joint_state = self.get_current_joint_state()
        return (
            joint_state.position[idx] * 100 / np.pi,
            joint_state.velocity[idx] * 100 / np.pi,
            joint_state.effort[idx] * 100 / np.pi
        )

    def _joint_name_to_index(self, joint_name: str) -> int:
        if not self._joint_name_to_index_dict:
            self._joint_name_to_index_dict = {name: i for i,
                                              name in enumerate(self.get_current_joint_state().name)}
        return self._joint_name_to_index_dict[joint_name]

    def _update_callback(self, joint_state: JointState) -> None:
        self._current_joint_state = joint_state

    def _get_observation_dict_for_joint_array(
            self, robot_keys: RobotOutputKeys) -> dict[str, np.ndarray]:
        result_dict = {}
        joint_name_array = robot_keys.joint_names
        joint_positions, joint_velocities, joint_loads = ([], [], [])

        # Extract data for each joint
        for joint_name in joint_name_array:
            pos, vel, load = self._get_joint_data(joint_name)
            joint_positions.append(pos)
            joint_velocities.append(vel)
            joint_loads.append(load)

        joint_positions = np.array([joint_positions])
        joint_velocities = np.array([joint_velocities])
        joint_loads = self._remove_nan_entries(joint_loads)

        result_dict[robot_keys.input_position_key] = joint_positions
        if robot_keys.input_velocity_key:
            result_dict[robot_keys.input_velocity_key] = joint_velocities
        if robot_keys.input_load_key:
            result_dict[robot_keys.input_load_key] = joint_loads
        return result_dict

    def _remove_nan_entries(self, values_in_radians):
        return np.array(
            [[0 if math.isnan(value) else value for value in values_in_radians]])
