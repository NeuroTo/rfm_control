from collections.abc import Sequence
import numpy as np
import cv2

from tng_control.model_adapter.mapper.input.model_input_mapper import ModelInputMapper
from tng_control.config.config_models.robot_config import RobotConfig
from tng_control.config.config_models.image_config import ImageConfig
from tng_control.observation_handler.observation_dto import Observations, JointState


class OctoInputMapper(ModelInputMapper):
    """
    Input mapper for Octo models.
    
    Transforms generic observations to Octo-specific format:
    - Joint angles pass through unchanged (in radians, no scaling)
    - Maps robot data to model-specific keys
    - Maps images from topic names to model-specific keys
    - Adds Octo-specific metadata (timestep_pad_mask)
    """
    
    def __init__(self, robot_configs: Sequence[RobotConfig], image_configs: Sequence[ImageConfig]):
        """
        Initialize OctoInputMapper.
        
        Args:
            robot_configs: Configuration for each robot (defines model-specific keys)
            image_configs: Image configurations defining topic→key mapping
        """
        self.robot_configs = robot_configs
        self.image_configs = image_configs
    
    def transform_observation(self, observations: Observations) -> dict[str, np.ndarray]:
        """
        Transform generic observations to Octo-specific format.
        
        Joint values pass through unchanged (in radians, no scaling).
        Adds timestep_pad_mask metadata.
        Resizes images to model-specific resolution.
        """
        transformed = {}
        
        # Transform robot joint data (no scaling for Octo, type-safe with dataclasses)
        for robot_obs in observations.robots:
            robot_config = self._find_robot_config(robot_obs.prefix)
            if robot_config:
                # Transform arm data
                transformed.update(self._transform_joint_data(
                    robot_obs.arm,
                    robot_config.arm_config
                ))
                # Transform gripper data
                transformed.update(self._transform_joint_data(
                    robot_obs.gripper,
                    robot_config.gripper_config
                ))
        
        # Transform images with model-specific resizing
        for image_cfg in self.image_configs:
            if image_cfg.topic_name in observations.images:
                raw_image = observations.images[image_cfg.topic_name]
                # Resize to model-specific resolution
                resized_image = cv2.resize(raw_image, image_cfg.resolution)
                # Apply model-specific transformation
                transformed[image_cfg.model_input_image_key] = image_cfg.transformation(resized_image)
        
        # Add Octo-specific metadata
        transformed["timestep_pad_mask"] = np.array([[True]])
        
        return transformed
    
    def _find_robot_config(self, prefix: str) -> RobotConfig | None:
        """Find robot config by prefix."""
        for config in self.robot_configs:
            if config.prefix == prefix:
                return config
        return None
    
    def _transform_joint_data(self, joint_data: JointState, keys_config) -> dict[str, np.ndarray]:
        """
        Transform joint data to Octo format (no scaling, raw radians).
        Uses type-safe JointState dataclass.
        """
        result = {}
        
        # Position (always present, no scaling)
        if keys_config.model_input_position_key:
            result[keys_config.model_input_position_key] = np.array([joint_data.positions])
        
        # Velocity (optional, no scaling)
        if keys_config.model_input_velocity_key:
            result[keys_config.model_input_velocity_key] = np.array([joint_data.velocities])
        
        # Load/Effort (optional, no scaling)
        if keys_config.model_input_load_key:
            result[keys_config.model_input_load_key] = joint_data.efforts
        
        return result

