from pathlib import Path

from rfm_control.config.config_loader import ConfigLoader
from rfm_control.config.config_schema import RfmConfigYaml
from rfm_control.config.config_models.robot_config import RobotConfig
from rfm_control.config.config_models.image_config import ImageConfig
from rfm_control.observation_handler.joint_state_handler import JointStateHandler
from rfm_control.observation_handler.image_handler import ImageHandler
from rfm_control.action_adapter.action_port import ActionPort
from rfm_control.model_adapter.model_port import ModelPort

from rfm_control.factories.model_adapter_factory import ModelAdapterFactory
from rfm_control.factories.action_adapter_factory import ActionAdapterFactory


from shared.robot_description_listener import get_robot_description_from_topic
from shared.ros2_control_joint_config import (
    parse_robot_description_to_joint_configs,
    Ros2ControlJointConfig
)


class AdapterFactory:
    """
    Factory for creating model and action adapters from YAML configuration.
    
    Example:
        factory = AdapterFactory()
        adapters1 = factory.create_adapters("config/gr00t_so101.yaml")
        adapters2 = factory.create_adapters("config/octo_ur5.yaml")
    """
    
    def __init__(
        self,
        model_adapter_factory: ModelAdapterFactory | None = None,
        action_adapter_factory: ActionAdapterFactory | None = None
    ):
        """
        Initialize adapter factory with sub-factories.
        
        Args:
            model_adapter_factory: Factory for creating model adapters
            action_adapter_factory: Factory for creating action adapters
            
        If any factory is None, a default instance will be created.
        """
        self.model_adapter_factory = model_adapter_factory or ModelAdapterFactory()
        self.action_adapter_factory = action_adapter_factory or ActionAdapterFactory()
        
        
    def _get_ros2_configs(self) -> list[Ros2ControlJointConfig]:
        """Get ROS2 control joint configurations from robot description."""
        robot_description: str = get_robot_description_from_topic()
        return parse_robot_description_to_joint_configs(robot_description)
    
    def _create_robot_configs(
        self, 
        yaml_config: RfmConfigYaml,
        ros2_configs: list[Ros2ControlJointConfig]
    ) -> list[RobotConfig]:
        """Convert YAML robot configs to RobotConfig objects with joint names."""
        robot_configs = []
        for yaml_robot in yaml_config.robots:
            # Find matching ROS2 config by prefix
            ros2_config = next(
                (rc for rc in ros2_configs if rc.prefix == yaml_robot.prefix),
                None
            )
            if ros2_config is None:
                raise ValueError(f"No ROS2 config found for prefix: {yaml_robot.prefix}")
            
            robot_config = ConfigLoader.to_robot_config(yaml_robot, ros2_config)
            robot_configs.append(robot_config)
        
        return robot_configs
    
    def _create_image_configs(self, yaml_config: RfmConfigYaml) -> list[ImageConfig]:
        """Convert YAML image configs to ImageConfig objects."""
        return [ConfigLoader.to_image_config(img) for img in yaml_config.images]
    
    
    def create_adapters(self, config_path: str | Path) -> tuple[ModelPort, ActionPort]:
        """
        Create model and action adapters based on YAML configuration.
        
        Args:
            config_path: Path to YAML configuration file
        
        Returns:
            Tuple of (ModelPort, ActionPort) configured according to YAML
            
        Raises:
            ValueError: If model type or configuration is invalid
            FileNotFoundError: If config file doesn't exist
        """
        # Load configuration
        yaml_config: RfmConfigYaml = ConfigLoader.load_yaml(config_path)
        ros2_configs: list[Ros2ControlJointConfig] = self._get_ros2_configs()
        robot_configs: list[RobotConfig] = self._create_robot_configs(yaml_config, ros2_configs)
        image_configs: list[ImageConfig] = self._create_image_configs(yaml_config)
        
        # Create handlers
        image_handler = ImageHandler(image_configs)
        joint_state_handler = JointStateHandler(robot_configs)
        
        # Create model adapter using factory
        model_adapter = self.model_adapter_factory.create(
            yaml_config.model.type,
            yaml_config,
            robot_configs,
            image_configs,
            image_handler,
            joint_state_handler
        )
        
        # Create action adapter using factory
        action_adapter = self.action_adapter_factory.create(
            yaml_config.action.type,
            robot_configs,
            joint_state_handler,
            yaml_config
        )
        
        return (model_adapter, action_adapter)
    