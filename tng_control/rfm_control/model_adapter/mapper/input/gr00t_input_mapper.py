from collections.abc import Sequence
import numpy as np
import cv2

from tng_control.rfm_control.model_adapter.mapper.input.model_input_mapper import ModelInputMapper
from tng_control.rfm_control.config.model_configs.robot_config import RobotConfig
from tng_control.rfm_control.observation_handler.image_feature import ImageFeature
from tng_control.rfm_control.observation_handler.observation_dto import Observations, RobotState, JointState


class Gr00tInputMapper(ModelInputMapper):
    """
    Input mapper for GR00T models.
    
    Transforms generic observations to GR00T-specific format:
    - Maps robot data to model-specific keys (from RobotConfig)
    - Scales joint angles from radians to policy scale: value * 100 / π
    - Maps images from topic names to model-specific keys
    """
    
    def __init__(self, robot_configs: Sequence[RobotConfig], image_features: Sequence[ImageFeature]):
        """
        Initialize Gr00tInputMapper.
        
        Args:
            robot_configs: Configuration for each robot (defines model-specific keys)
            image_features: Image features defining topic→key mapping
        """
        self.robot_configs = robot_configs
        self.image_features = image_features
    
    def transform_observation(self, observations: Observations) -> dict[str, np.ndarray]:
        """
        Transform generic observations to GR00T-specific format.
        
        Applies:
        - Joint position/velocity/effort scaling: radians * 100 / π
        - Mapping to model-specific keys from RobotConfig
        - Image resizing to model-specific resolution
        - Image transformation and key mapping
        """
        transformed = {}
        
        # Transform robot joint data (type-safe with dataclasses)
        for robot_obs in observations.robots:
            robot_config = self._find_robot_config(robot_obs.prefix)
            if robot_config:
                # Transform arm data
                transformed.update(self._transform_joint_data(
                    robot_obs.arm,
                    robot_config.arm_keys
                ))
                # Transform gripper data
                transformed.update(self._transform_joint_data(
                    robot_obs.gripper,
                    robot_config.gripper_keys
                ))
        
        # Transform images with model-specific resizing
        for image_ft in self.image_features:
            if image_ft.topic_name in observations.images:
                raw_image = observations.images[image_ft.topic_name]
                # Resize to model-specific resolution
                resized_image = cv2.resize(raw_image, image_ft.resolution)
                # Apply model-specific transformation
                transformed[image_ft.model_input_image_key] = image_ft.transformation(resized_image)
        
        return transformed
    
    def _find_robot_config(self, prefix: str) -> RobotConfig | None:
        """Find robot config by prefix."""
        for config in self.robot_configs:
            if config.prefix == prefix:
                return config
        return None
    
    def _transform_joint_data(self, joint_data: JointState, keys_config) -> dict[str, np.ndarray]:
        """
        Transform joint data to GR00T format with scaling.
        
        Converts from radians to policy scale: value * 100 / π
        Uses type-safe JointState dataclass.
        """
        result = {}
        
        # Position (always present)
        if keys_config.input_position_key:
            positions = joint_data.positions * 100 / np.pi
            result[keys_config.input_position_key] = np.array([positions])
        
        # Velocity (optional)
        if keys_config.input_velocity_key:
            velocities = joint_data.velocities * 100 / np.pi
            result[keys_config.input_velocity_key] = np.array([velocities])
        
        # Load/Effort (optional)
        if keys_config.input_load_key:
            efforts = joint_data.efforts * 100 / np.pi
            result[keys_config.input_load_key] = efforts  # Already in correct shape from handler
        
        return result

