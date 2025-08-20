import math
import numpy as np
from sensor_msgs.msg import JointState

from tng_control.rfm_control_status_code import JointStatesNotAvailableException
from tng_control.config.model_configs.model_config import ModelConfig


class JointStateHandler:

    @property
    def joint_name_to_index(self) -> dict[str, int]:
        if not self._joint_name_to_index:
            self._joint_name_to_index = {name: i for i,
                                         name in enumerate(self.get_current_joint_state().name)}
        return self._joint_name_to_index

    def __init__(self, config: ModelConfig) -> None:
        self.joint_state_topic = config.joint_state_topic
        self.config = config
        self._current_joint_state: JointState | None = None
        self._joint_name_to_index: dict[str, int] = {}

    def update_joint_state_callback(self, joint_state: JointState) -> None:
        self._current_joint_state = joint_state

    def get_current_joint_state(self) -> JointState:
        if not self._current_joint_state:
            raise JointStatesNotAvailableException()
        return self._current_joint_state

    def get_robot_state(self, robot_name: str) -> list[float]:
        joint_state = self.get_current_joint_state()
        return [joint_state.position[self.joint_name_to_index[joint]] for joint in self.config.joint_names_for_robot(robot_name)]

    def map_joint_states_to_observation_dict(self) -> dict[str, np.ndarray]:
        """Map current joint states to an observation dictionary format expected by the model."""
        result_dict = {}

        for robot_index in range(len(self.config.robot_ids)):
            joint_name_array = self.config.joint_names[robot_index]

            # Initialize lists for this robot
            joint_positions = []
            joint_velocities = []
            joint_loads = []

            # Extract data for each joint
            for joint_name in joint_name_array:

                pos, vel, load = self._get_joint_data(joint_name)
                joint_positions.append(pos)
                joint_velocities.append(vel)
                joint_loads.append(load)

            result_dict[self.config.arm_keys.input_position_keys[robot_index]
                        ] = np.array([joint_positions]) * 100 / np.pi
            if self.config.arm_keys.input_velocity_keys:
                result_dict[self.config.arm_keys.input_velocity_keys[robot_index]
                            ] = np.array([joint_velocities]) * 100 / np.pi

            if self.config.arm_keys.input_load_keys:
                result_dict[self.config.arm_keys.input_load_keys[robot_index]] = np.array(
                    [[0 if math.isnan(joint_load) else joint_load for joint_load in joint_loads]]) * 100 / np.pi

            # gripper
            gripper_pos, gripper_vel, gripper_load = self._get_joint_data(
                self.config.gripper_names[robot_index])

            result_dict[self.config.gripper_keys.input_position_keys[robot_index]
                        ] = np.array([[gripper_pos * 100 / np.pi]])
            if self.config.gripper_keys.input_velocity_keys:
                result_dict[self.config.gripper_keys.input_velocity_keys[robot_index]] = np.array([[
                    gripper_vel * 100 / np.pi]])
            if self.config.gripper_keys.input_load_keys:
                result_dict[self.config.gripper_keys.input_load_keys[robot_index]] = np.array([[
                    0.0 if math.isnan(gripper_load) else gripper_load * 100 / np.pi]])

        return result_dict

    def _get_joint_data(self, joint_name: str) -> tuple[float, float, float]:
        idx = self.joint_name_to_index[joint_name]
        joint_state = self.get_current_joint_state()
        return (
            joint_state.position[idx],
            joint_state.velocity[idx],
            joint_state.effort[idx]
        )
