import yaml
from typing import ClassVar, Literal
from dataclasses import dataclass
from shared.package_paths import TNG_ROBOT_ARMS_BRINGUP

SINGLE_ARM_ROBOT_MODELS = ['igus_rebel_6dof', 'panda', 'so101', 'ur5']
DUAL_ARM_ROBOT_MODELS = ['so101_bimanual']

@dataclass
class RobotModelConfig:
    robot_model: Literal['igus_rebel_6dof', 'panda', 'so101', 'so101_bimanual', 'ur5']
    gripper_model: Literal['schunk', 'panda']
    prefixes: list[str]

    _instance: ClassVar["RobotModelConfig"] = None
   
    @classmethod
    def instance(cls) -> "RobotModelConfig":
        """
        returns Singleton instance of RobotModelConfig filled with the values from tng_robot_arms_bringup/config/robot_model_config.yaml.
        """
        if cls._instance is None:
            with open(f'{TNG_ROBOT_ARMS_BRINGUP}/config/robot_model_config.yaml', 'r') as file:
                robot_model_config_dict = yaml.safe_load(file)

            required_fields = ['robot_model', 'gripper_model', 'prefixes']
            for field in required_fields:
                if field not in robot_model_config_dict:
                    raise ValueError(f"Missing '{field}' in {TNG_ROBOT_ARMS_BRINGUP}/config/robot_model_config.yaml")
                
            robot_model=robot_model_config_dict['robot_model']
            gripper_model=robot_model_config_dict['gripper_model']
           
            if robot_model in SINGLE_ARM_ROBOT_MODELS:
                prefixes = [robot_model_config_dict['prefixes']['single_arm']]
            elif robot_model in DUAL_ARM_ROBOT_MODELS:
                prefixes = [robot_model_config_dict['prefixes']['dual_arm']['left'], robot_model_config_dict['prefixes']['dual_arm']['right']]

            cls._instance = cls(robot_model, gripper_model, prefixes)
        return cls._instance
