import numpy as np
from typing_extensions import override
from tng_control.rfm_control.model_adapter.observation_handler.image_feature import ImageFeature
from tng_control.rfm_control.config.model_configs.model_config import ModelConfig
from tng_control.rfm_control.config.model_configs.robot_config import RobotConfig, RobotOutputKeys


class Gr00tConfig(ModelConfig):

    @property
    def port(self) -> int:
        return 8043


class Gr00tUR5Config(Gr00tConfig):
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
                                  )
                                  )]

    @property
    @override
    def image_features(self) -> list[ImageFeature]:
        return [
            ImageFeature(
               "video.global_side_cam", (640, 480), "/camera_global_side/rgb/image_raw/compressed",
               transformation=lambda x: np.array([x])
            ),
            ImageFeature(
               "video.global_front_cam", (640, 480), "/camera_global_front/rgb/image_raw/compressed",
               transformation=lambda x: np.array([x])
            ),
            ImageFeature(
               "video.wrist_cam", (640, 480), "/camera_wrist/rgb/image_raw/compressed",
               transformation=lambda x: np.array([x])
            )
        ]

    @property
    @override
    def joint_state_topic(self) -> str:
        return "/joint_states"


class Gr00tSO101Config(Gr00tConfig):

    _robot_configs = [RobotConfig(prefix="",
                                  group_name="arm",
                                  frame_id="world",
                                  arm_keys=RobotOutputKeys(
                                      topic_name="/arm_controller/follow_joint_trajectory",
                                      input_position_key="state.single_arm",
                                      input_velocity_key="",
                                      input_load_key="",
                                      output_position_key="action.single_arm",
                                      output_velocity_key="",
                                      joint_names=[]
                                  ),
                                  gripper_keys=RobotOutputKeys(
                                      topic_name="/gripper_controller/gripper_cmd",
                                      input_position_key="state.gripper",
                                      input_velocity_key="",
                                      input_load_key="",
                                      output_position_key="action.gripper",
                                      output_velocity_key="",
                                      joint_names=[]
                                  )
                                  )]

    @property
    @override
    def image_features(self) -> list[ImageFeature]:
        return [
            ImageFeature(
                "video.wrist", (640, 480), "/wrist/image_raw/compressed", lambda x: np.array([x]),
            ),
            ImageFeature(
                "video.global", (640, 480), "/global_front/image_raw/compressed", lambda x: np.array([x]),
            ),
        ]

    @property
    @override
    def joint_state_topic(self) -> str:
        return "/joint_states"


class Gr00tSo101DualArmConfig(Gr00tSO101Config):

    _robot_configs = [RobotConfig(prefix="right_arm",
                                  group_name="arm",
                                  frame_id="world",
                                  arm_keys=RobotOutputKeys(
                                      topic_name="/right_arm_controller/follow_joint_trajectory",
                                      input_position_key="state.single_arm",
                                      input_velocity_key="",
                                      input_load_key="",
                                      output_position_key="action.single_arm",
                                      output_velocity_key="",
                                      joint_names=[]
                                  ),
                                  gripper_keys=RobotOutputKeys(
                                      topic_name="/right_arm_controller/gripper_cmd",
                                      input_position_key="state.gripper",
                                      input_velocity_key="",
                                      input_load_key="",
                                      output_position_key="action.gripper",
                                      output_velocity_key="",
                                      joint_names=[]
                                  )
                                  ),
                      RobotConfig(prefix="left_arm",
                                  group_name="arm",
                                  frame_id="world",
                                  arm_keys=RobotOutputKeys(
                                      topic_name="/left_arm_controller/follow_joint_trajectory",
                                      input_position_key="state.right_gripper_pos",
                                      input_velocity_key="state.right_gripper_vel",
                                      input_load_key="state.right_gripper_load",
                                      output_position_key="action.right_gripper_pos",
                                      output_velocity_key="action.right_gripper_vel",
                                      joint_names=[]
                                  ),
                                  gripper_keys=RobotOutputKeys(
                                      topic_name="/left_arm_controller/gripper_cmd",
                                      input_position_key="state.left_gripper_pos",
                                      input_velocity_key="state.left_gripper_vel",
                                      input_load_key="state.left_gripper_load",
                                      output_position_key="action.left_gripper_pos",
                                      output_velocity_key="action.left_gripper_vel",
                                      joint_names=[]
                                  )
                                  )]

    @property
    @override
    def image_features(self) -> list[ImageFeature]:
        return [
            ImageFeature(
                "video.right_arm_wrist", (640, 480), "/right_arm_wrist/image_raw/compressed", lambda x: np.array([x]),
            ),
            ImageFeature(
                "video.left_arm_wrist", (640, 480), "/left_arm_wrist/image_raw/compressed", lambda x: np.array([x]),
            ),
            ImageFeature(
                "video.global1", (640, 480), "/global1/image_raw/compressed", lambda x: np.array([x]),
            ),
            ImageFeature(
                "video.global2", (640, 480), "/global2/image_raw/compressed", lambda x: np.array([x]),
            ),
        ]

