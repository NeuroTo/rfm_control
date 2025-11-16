"""Factory for creating adapters from YAML configuration."""
from trajectory_msgs.msg._joint_trajectory import JointTrajectory


from pathlib import Path
from collections.abc import Sequence

from tng_control.rfm_control.config.config_loader import ConfigLoader
from tng_control.rfm_control.config.config_schema import RfmConfigYaml
from tng_control.rfm_control.config.model_configs.robot_config import RobotConfig
from tng_control.rfm_control.config.model_configs.image_config import ImageConfig
from tng_control.rfm_control.observation_handler.joint_state_handler import JointStateHandler
from tng_control.rfm_control.observation_handler.image_handler import ImageHandler
from tng_control.rfm_control.action_adapter.robot import Robot
from tng_control.rfm_control.action_adapter.action_port import ActionPort
from tng_control.rfm_control.action_adapter.follow_joint_trajectory_adapter import FollowJointTrajectoryAdapter
from tng_control.rfm_control.action_adapter.mapper.absolute_joint_action_mapper import AbsoluteJointActionMapper
from tng_control.action_executor.joint_trajectory_action_executor import JointTrajectoryActionExecutor
from tng_control.action_executor.gripper_action_executor import GripperActionExecutor
from tng_control.rfm_control.model_adapter.model_port import ModelPort

# GR00T imports
from tng_control.rfm_control.model_adapter.gr00t_adapter import Gr00tAdapter
from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_client import Gr00tClient
from tng_control.rfm_control.model_adapter.mapper.input.gr00t_input_mapper import Gr00tInputMapper
from tng_control.rfm_control.model_adapter.mapper.output.joint_state_mapper import (
    Gr00tJointStateMapper, Gr00tJointStateMapperRTC
)

# Octo imports
from tng_control.rfm_control.model_adapter.octo_adapter import OctoAdapter
from tng_control.rfm_control.model_adapter.model_clients.octo.octo_client import OctoClient
from tng_control.rfm_control.model_adapter.mapper.input.octo_input_mapper import OctoInputMapper
from tng_control.rfm_control.model_adapter.mapper.output.delta_endeffector_mapper import OctoDeltaEndeffectorMapper

# Test clients (mocks)
from tng_control.test.model_adapter.model_clients.gr00t_client_mock import Gr00tRTCClientMock
from tng_control.test.model_adapter.model_clients.octo_client_mock import OctoClientMock

from tng_robot_arms_shared.robot_description_listener import get_robot_description_from_topic
from tng_robot_arms_shared.ros2_control_joint_config import (
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
    
    def _create_robots(self, robot_configs: list[RobotConfig]) -> Sequence[Robot]:
        """Create robots with appropriate action mappers."""
        return [
            Robot[JointTrajectory](
                prefix=robot.prefix,
                action_mapper=AbsoluteJointActionMapper(robot.arm_config.joint_names),
                arm_action_executor=JointTrajectoryActionExecutor(robot.arm_config.topic_name),
                gripper_action_executor=GripperActionExecutor(robot.gripper_config.topic_name)
            )
            for robot in robot_configs
        ]
    
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
        
        # Create robots
        robots = self._create_robots(robot_configs)
        
        # Model type to factory method mapping
        model_factory_registry = {
            'gr00t': self._create_gr00t_adapter,
            'octo': self._create_octo_adapter,
        }
        
        # Create adapters based on model type
        model_type = yaml_config.model.type
        factory_method = model_factory_registry.get(model_type)
        
        if factory_method is None:
            raise ValueError(
                f"Unknown model type: '{model_type}'. "
                f"Supported types: {list[str](model_factory_registry.keys())}"
            )
        
        model_adapter = factory_method(
            yaml_config, robot_configs, image_configs, image_handler, joint_state_handler
        )
        
        # Create action adapter
        action_adapter = FollowJointTrajectoryAdapter(robots, joint_state_handler)
        
        return (model_adapter, action_adapter)
    
    def _create_gr00t_adapter(
        self,
        yaml_config: RfmConfigYaml,
        robot_configs: list[RobotConfig],
        image_configs: list[ImageConfig],
        image_handler: ImageHandler,
        joint_state_handler: JointStateHandler
    ) -> ModelPort:
        """Create GR00T model adapter."""
        # Import base class
        from tng_control.rfm_control.config.model_client_config_base import Gr00tConfigBase
        
        # Create config implementation for GR00T client
        class Gr00tConfigFromYaml(Gr00tConfigBase):
            """Config implementation for YAML-based GR00T configuration."""
            def __init__(self, port: int):
                self._port = port
            
            @property
            def port(self) -> int:
                return self._port
        
        model_config = Gr00tConfigFromYaml(yaml_config.model.port)
        
        # Create mappers
        input_mapper = Gr00tInputMapper(robot_configs, image_configs)
        
        mapper_type = yaml_config.model.mapper_type
        if mapper_type == 'rtc':
            output_mapper = Gr00tJointStateMapperRTC(robot_configs)
        else:
            output_mapper = Gr00tJointStateMapper(robot_configs)
        
        # Create client
        client_type = yaml_config.model.client_type
        if client_type == 'mock':
            model_client = Gr00tRTCClientMock(model_config)
        else:
            model_client = Gr00tClient(model_config)
        
        return Gr00tAdapter(
            model_client,
            input_mapper,
            output_mapper,
            [image_handler, joint_state_handler]
        )
    
    def _create_octo_adapter(
        self,
        yaml_config: RfmConfigYaml,
        robot_configs: list[RobotConfig],
        image_configs: list[ImageConfig],
        image_handler: ImageHandler,
        joint_state_handler: JointStateHandler
    ) -> ModelPort:
        """Create Octo model adapter."""
        # Import base class
        from tng_control.rfm_control.config.model_client_config_base import OctoConfigBase
        
        # Create config implementation for Octo client
        class OctoConfigFromYaml(OctoConfigBase):
            """Config implementation for YAML-based Octo configuration."""
            @property
            def model_path(self) -> str:
                return "hf://rail-berkeley/octo-small-1.5"
            
            def get_dataset_statistics(self, model):
                return model.dataset_statistics["berkeley_autolab_ur5"]["action"]
        
        model_config = OctoConfigFromYaml()
        
        # Create mappers
        input_mapper = OctoInputMapper(robot_configs, image_configs)
        output_mapper = OctoDeltaEndeffectorMapper(robot_configs)
        
        # Create client
        client_type = yaml_config.model.client_type
        if client_type == 'mock':
            model_client = OctoClientMock()
        else:
            model_client = OctoClient(model_config)
        
        return OctoAdapter(
            model_client,
            input_mapper,
            output_mapper,
            [image_handler, joint_state_handler]
        )

