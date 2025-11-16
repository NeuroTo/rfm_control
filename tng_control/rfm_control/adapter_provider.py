from typing import Literal

from tng_control.rfm_control.config.model_configs.octo_config import OctoUR5Config
from tng_control.rfm_control.config.model_configs.gr00t_config import Gr00tSO101Config, Gr00tUR5Config
from tng_control.rfm_control.action_adapter.action_port import ActionPort
from tng_control.rfm_control.model_adapter.model_port import ModelPort
from tng_control.rfm_control.factories.gr00t_adapter_factory import Gr00tAdapterFactory
from tng_control.rfm_control.factories.octo_adapter_factory import OctoAdapterFactory
from tng_control.test.config.model_configs.gr00t_config import ConstGr00t, ConstGr00tSo101DualArmConfig

from tng_robot_arms_shared.robot_description_listener import get_robot_description_from_topic
from tng_robot_arms_shared.ros2_control_joint_config import parse_robot_description_to_joint_configs

ConfigStrings = Literal['gr00t_so101', 'gr00t_so101_rtc', 'gr00t_ur5',
                        "const", "dual_const", "so101_dual", 'octo_ur5', "octo_ur5_constant"]


class AdapterProvider:
    """
    Provider for creating model and action adapters based on configuration strings.
    
    Coordinates the creation of appropriate adapters for different robot foundation models
    by delegating to specific factory classes.
    """

    def get_adapters(self, config_string: ConfigStrings) -> tuple[ModelPort, ActionPort]:
        """
        Get adapters for the model and action port for the given config string.
        
        Model and action adapters are coupled to each other because the model configuration 
        needs to match the motion executor configuration. E.g. if the model is trained for 
        delta actions, the action adapter needs to process those delta actions correctly.
        
        Args:
            config_string: Configuration identifier specifying which model and setup to use
            
        Returns:
            Tuple of (ModelPort, ActionPort) configured for the specified setup
            
        Raises:
            ValueError: If the config_string is not recognized
        """
        robot_description = get_robot_description_from_topic()
        ros2_control_joint_configs = parse_robot_description_to_joint_configs(robot_description)

        match config_string:
            case 'gr00t_so101':
                return Gr00tAdapterFactory(
                    Gr00tSO101Config(ros2_control_joint_configs)).create_default()
            case 'gr00t_so101_rtc':
                return Gr00tAdapterFactory(
                    Gr00tSO101Config(ros2_control_joint_configs)).create_rtc()
            case 'const':
                return Gr00tAdapterFactory(
                    ConstGr00t(ros2_control_joint_configs)).create_rtc_constant()
            case 'dual_const':
                return Gr00tAdapterFactory(
                    ConstGr00tSo101DualArmConfig(ros2_control_joint_configs)).create_so101_constant_dual()
            case 'gr00t_ur5':
                return Gr00tAdapterFactory(Gr00tUR5Config(ros2_control_joint_configs)).create_default()
            case 'octo_ur5':
                return OctoAdapterFactory(OctoUR5Config(ros2_control_joint_configs)).create_default()
            case 'octo_ur5_constant':
                return OctoAdapterFactory(
                    OctoUR5Config(ros2_control_joint_configs)).create_constant_client()
            case _:
                raise ValueError(f"Invalid config string: {config_string}")
