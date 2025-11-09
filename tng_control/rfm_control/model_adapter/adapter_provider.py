from collections.abc import Sequence
from typing import Literal

from tng_control.rfm_control.model_adapter.observation_handler.joint_state_handler import JointStateHandler
from tng_control.rfm_control.model_adapter.observation_handler.image_handler import ImageHandler
from tng_control.rfm_control.action_adapter.robot import Robot
from tng_control.rfm_control.action_adapter.joint_state_subscriber import JointStateSubscriber
from tng_control.rfm_control.model_adapter.model_clients.octo.octo_client import OctoClient
from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_client import Gr00tClient
from tng_control.rfm_control.config.model_configs.octo_config import OctoConfig, OctoUR5Config
from tng_control.rfm_control.config.model_configs.gr00t_config import Gr00tConfig, Gr00tSO101Config, Gr00tUR5Config
from tng_control.rfm_control.model_adapter.mapper.joint_state_mapper import Gr00tJointStateMapper, Gr00tJointStateMapperRTC
from tng_control.rfm_control.model_adapter.mapper.delta_endeffector_mapper import OctoDeltaEndeffectorMapper
from tng_control.rfm_control.action_adapter.action_port import ActionPort
from tng_control.rfm_control.action_adapter.follow_joint_trajectory_adapter import FollowJointTrajectoryAdapter
from tng_control.rfm_control.model_adapter.gr00t_adapter import Gr00tAdapter
from tng_control.rfm_control.model_adapter.mapper.model_output_mapper import ModelOutputMapper
from tng_control.rfm_control.model_adapter.octo_adapter import OctoAdapter
from tng_control.rfm_control.model_adapter.model_port import ModelPort
from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_model_client import Gr00tModelClient
from tng_control.rfm_control.model_adapter.model_clients.octo.octo_model_client import OctoModelClient
from tng_control.test.model_adapter.model_clients.constant_gr00t_client import ConstantGr00tRTCClient
from tng_control.test.model_adapter.model_clients.constant_gr00t_client_dual import ConstantDualGr00tClient
from tng_control.test.config.model_configs.gr00t_config import ConstGr00t, ConstGr00tSo101DualArmConfig
from tng_control.test.model_adapter.model_clients.constant_octo_client import ConstantOctoClient

from tng_robot_arms_shared import get_robot_description_from_topic, parse_robot_description_to_joint_configs


ConfigStrings = Literal['gr00t_so101', 'gr00t_so101_rtc', 'gr00t_ur5',
                        "const", "dual_const", "so101_dual", 'octo_ur5', "octo_ur5_constant"]


class Gr00tAdapterFactory:

    config: Gr00tConfig

    def __init__(self, config: Gr00tConfig):
        self.config = config

    def _create_robots(self) -> Sequence[Robot]:
        return [Robot.from_robot_config(robot) for robot in self.config.robot_configs]

    def _create_robots_delta(self) -> Sequence[Robot]:
        return [Robot.from_robot_config_delta_action(robot) for robot in self.config.robot_configs]

    def _create(self, model_output_mapper: ModelOutputMapper,
                model_client: Gr00tModelClient) -> tuple[ModelPort, ActionPort]:

        image_handler = ImageHandler(self.config.image_features)
        joint_state_handler = JointStateHandler(
            self.config.robot_configs, self.config.joint_state_topic)
        joint_state_subscriber = JointStateSubscriber(self.config.joint_state_topic)
        robots = self._create_robots()
        model_adapter = Gr00tAdapter(model_client, model_output_mapper, [image_handler, joint_state_handler])
        action_adapter = FollowJointTrajectoryAdapter(robots, joint_state_subscriber)

        return (model_adapter, action_adapter)

    def create_default(self) -> tuple[ModelPort, ActionPort]:
        model_output_mapper = Gr00tJointStateMapper(self.config.robot_configs)
        return self._create(model_output_mapper, Gr00tClient(self.config))

    def create_rtc(self) -> tuple[ModelPort, ActionPort]:
        model_output_mapper = Gr00tJointStateMapperRTC(self.config.robot_configs)
        return self._create(model_output_mapper, Gr00tClient(self.config))

    def create_rtc_constant(self) -> tuple[ModelPort, ActionPort]:
        model_output_mapper = Gr00tJointStateMapperRTC(self.config.robot_configs)
        return self._create(model_output_mapper,  ConstantGr00tRTCClient(self.config))

    def create_so101_constant_dual(self) -> tuple[ModelPort, ActionPort]:
        model_output_mapper = Gr00tJointStateMapperRTC(self.config.robot_configs)
        return self._create(model_output_mapper, ConstantDualGr00tClient(self.config))


class OctoAdapterFactory:

    config: OctoConfig

    def __init__(self, config: OctoConfig):
        self.config = config

    def _create(self, model_client: OctoModelClient) -> tuple[ModelPort, ActionPort]:
        image_handler = ImageHandler(self.config.image_features)
        joint_state_handler = JointStateHandler(
            self.config.robot_configs, self.config.joint_state_topic)
        joint_state_subscriber = JointStateSubscriber(self.config.joint_state_topic)
        model_output_mapper = OctoDeltaEndeffectorMapper(self.config.robot_configs)
        model_adapter = OctoAdapter(model_client, model_output_mapper, [image_handler])
        robots = [Robot.from_robot_config_delta_action(robot_config)
                  for robot_config in self.config.robot_configs]
        action_adapter = FollowJointTrajectoryAdapter(robots, joint_state_subscriber)
        return (model_adapter, action_adapter)

    def create_default(self) -> tuple[ModelPort, ActionPort]:
        model_client = OctoClient(self.config)
        return self._create(model_client)

    def create_constant_client(self) -> tuple[ModelPort, ActionPort]:
        model_client = ConstantOctoClient()
        return self._create(model_client)


def get_adapters(config_string: ConfigStrings) -> tuple[ModelPort, ActionPort]:
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
