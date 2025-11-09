import numpy as np
from typing_extensions import override

from sensor_msgs.msg import Image

from tng_control.rfm_control.observation_handler.image_feature import ImageFeature
from tng_control.rfm_control.config.model_configs.model_config import ModelConfig
from tng_control.rfm_control.config.model_configs.robot_config import RobotOutputKeys, RobotConfig


class OctoConfig(ModelConfig):

    @property
    def model_path(self) -> str:
        return "hf://rail-berkeley/octo-small-1.5"

    def get_dataset_statistics(self, model):
        return model.dataset_statistics["berkeley_autolab_ur5"]["action"]


class OctoUR5Config(OctoConfig):

    _robot_configs = [RobotConfig(prefix="",
                                  group_name="arm",
                                  frame_id="world",
                                  arm_keys=RobotOutputKeys(
                                      topic_name="/arm_controller/follow_joint_trajectory",
                                      input_position_key="state.joint_positions",
                                      input_velocity_key="",
                                      input_load_key="",
                                      output_position_key="action.joint_positions",
                                      output_velocity_key="",
                                      joint_names=[]
                                  ),
                                  gripper_keys=RobotOutputKeys(
                                      topic_name="/gripper_controller/gripper_cmd",
                                      input_position_key="state.finger_positions",
                                      input_velocity_key="",
                                      input_load_key="",
                                      output_position_key="action.finger_positions",
                                      output_velocity_key="",
                                      joint_names=[]
                                  ))]

    @property
    @override
    def image_features(self) -> list[ImageFeature]:
        return [
            ImageFeature(
                model_input_image_key="image_primary",
                resolution=(256, 256),
                topic_name="/camera_global2/rgb/image_raw",
                transformation=lambda x: np.array([np.array([x])]),
                image_type=Image)
        ]

    @property
    @override
    def joint_state_topic(self) -> str:
        return "/joint_states"
