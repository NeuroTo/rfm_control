"""Configuration loader for YAML-based robot foundation model configs."""
import yaml
from pathlib import Path
from typing import Callable
import numpy as np
from sensor_msgs.msg import Image, CompressedImage
from pydantic import ValidationError

from tng_control.rfm_control.config.config_schema import RfmConfigYaml, ImageConfigYaml, RobotConfigYaml
from tng_control.rfm_control.config.config_models.robot_config import (
    RobotConfig, ActuatorConfig
)
from tng_control.rfm_control.config.config_models.image_config import ImageConfig
from tng_robot_arms_shared.ros2_control_joint_config import Ros2ControlJointConfig


class ConfigLoader:
    """
    Loads and converts YAML configuration to runtime objects.
    
    Handles transformation of YAML schema to model configs, robot configs,
    and image configs with appropriate transformations and types.
    """
    
    # Image transformation functions
    _TRANSFORMATIONS: dict[str, Callable[[np.ndarray], np.ndarray]] = {
        "identity": lambda x: x,
        "gr00t": lambda x: np.array([np.array([x])]),
        "octo": lambda x: np.array([np.array([x])]),
    }
    
    _IMAGE_TYPES = {
        "raw": Image,
        "compressed": CompressedImage,
    }
    
    @staticmethod
    def load_yaml(config_path: str | Path) -> RfmConfigYaml:
        """
        Load and validate YAML configuration file using Pydantic.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Validated Pydantic configuration model
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is malformed
            ValidationError: If configuration doesn't match schema
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        try:
            # Pydantic automatically validates the data
            return RfmConfigYaml(**data)
        except ValidationError as e:
            # Provide helpful error message with file context
            raise ValueError(
                f"Configuration validation failed for {config_path}:\n{e}"
            ) from e
    
    
    @staticmethod
    def to_robot_config(
        yaml_config: RobotConfigYaml,
        ros2_config: Ros2ControlJointConfig
    ) -> RobotConfig:
        """
        Convert YAML robot config to RobotConfig with joint names from ROS2.
        
        Args:
            yaml_config: Robot configuration from YAML
            ros2_config: Joint configuration from ROS2 control
            
        Returns:
            RobotConfig with populated joint names
        """
        arm_config = ActuatorConfig(
            topic_name=yaml_config.arm.topic_name,
            joint_names=ros2_config.arm_joint_names,
            model_input_position_key=yaml_config.arm.model_input_position_key,
            model_input_velocity_key=yaml_config.arm.model_input_velocity_key,
            model_input_load_key=yaml_config.arm.model_input_load_key,
            model_output_position_key=yaml_config.arm.model_output_position_key,
            model_output_velocity_key=yaml_config.arm.model_output_velocity_key,
        )
        
        gripper_config = ActuatorConfig(
            topic_name=yaml_config.gripper.topic_name,
            joint_names=[ros2_config.gripper_joint_name],
            model_input_position_key=yaml_config.gripper.model_input_position_key,
            model_input_velocity_key=yaml_config.gripper.model_input_velocity_key,
            model_input_load_key=yaml_config.gripper.model_input_load_key,
            model_output_position_key=yaml_config.gripper.model_output_position_key,
            model_output_velocity_key=yaml_config.gripper.model_output_velocity_key,
        )
        
        return RobotConfig(
            prefix=yaml_config.prefix,
            group_name=yaml_config.group_name,
            frame_id=yaml_config.frame_id,
            arm_config=arm_config,
            gripper_config=gripper_config,
            joint_state_topic=yaml_config.joint_state_topic,
            time_between_goals=yaml_config.time_between_goals
        )
    
    @staticmethod
    def to_image_config(yaml_config: ImageConfigYaml) -> ImageConfig:
        """
        Convert YAML image config to ImageConfig.
        
        Args:
            yaml_config: Image configuration from YAML
            
        Returns:
            ImageConfig with appropriate transformation and type
        """
        transformation = ConfigLoader._TRANSFORMATIONS.get(
            yaml_config.transformation,
            ConfigLoader._TRANSFORMATIONS["identity"]
        )
        
        image_type = ConfigLoader._IMAGE_TYPES.get(
            yaml_config.image_type,
            CompressedImage
        )
        
        return ImageConfig(
            model_input_image_key=yaml_config.model_input_key,
            resolution=yaml_config.resolution,  # Already tuple from Pydantic validator
            topic_name=yaml_config.topic_name,
            transformation=transformation,
            image_type=image_type
        )

