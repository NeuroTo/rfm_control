from collections.abc import Sequence

from tng_control.rfm_control.observation_handler.joint_state_handler import JointStateHandler
from tng_control.rfm_control.observation_handler.image_handler import ImageHandler
from tng_control.rfm_control.action_adapter.robot import Robot
from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_client import Gr00tClient
from tng_control.rfm_control.config.model_configs.gr00t_config import Gr00tConfig
from tng_control.rfm_control.model_adapter.mapper.input.gr00t_input_mapper import Gr00tInputMapper
from tng_control.rfm_control.model_adapter.mapper.output.joint_state_mapper import Gr00tJointStateMapper, Gr00tJointStateMapperRTC
from tng_control.rfm_control.action_adapter.action_port import ActionPort
from tng_control.rfm_control.action_adapter.follow_joint_trajectory_adapter import FollowJointTrajectoryAdapter
from tng_control.rfm_control.action_adapter.mapper.absolute_joint_action_mapper import AbsoluteJointActionMapper
from tng_control.rfm_control.action_adapter.mapper.delta_endeffector_action_mapper import DeltaEndeffectorActionMapper
from tng_control.action_executor.joint_trajectory_action_executor import JointTrajectoryActionExecutor
from tng_control.action_executor.gripper_action_executor import GripperActionExecutor
from tng_control.rfm_control.model_adapter.gr00t_adapter import Gr00tAdapter
from tng_control.rfm_control.model_adapter.mapper.output.model_output_mapper import ModelOutputMapper
from tng_control.rfm_control.model_adapter.model_port import ModelPort
from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_model_client import Gr00tModelClient
from tng_control.test.model_adapter.model_clients.constant_gr00t_client import ConstantGr00tRTCClient
from tng_control.test.model_adapter.model_clients.constant_gr00t_client_dual import ConstantDualGr00tClient


class Gr00tAdapterFactory:
    """
    Factory for creating GR00T model and action adapters.
    
    Provides different configurations for GR00T models including:
    - Default joint state mapping
    - Real-time control (RTC) mapping
    - Constant test clients
    """

    def __init__(self, config: Gr00tConfig):
        self.config = config

    def _create_robots(self) -> Sequence[Robot]:
        """Create robots with absolute joint action mapper."""
        return [
            Robot(
                prefix=robot.prefix,
                action_mapper=AbsoluteJointActionMapper(robot.arm_keys.joint_names),
                arm_action_executor=JointTrajectoryActionExecutor(robot.arm_keys.topic_name),
                gripper_action_executor=GripperActionExecutor(robot.gripper_keys.topic_name)
            )
            for robot in self.config.robot_configs
        ]

    def _create_robots_delta(self) -> Sequence[Robot]:
        """Create robots with delta endeffector action mapper."""
        return [
            Robot(
                prefix=robot.prefix,
                action_mapper=DeltaEndeffectorActionMapper(robot),
                arm_action_executor=JointTrajectoryActionExecutor(robot.arm_keys.topic_name),
                gripper_action_executor=GripperActionExecutor(robot.gripper_keys.topic_name)
            )
            for robot in self.config.robot_configs
        ]

    def _create(self, model_output_mapper: ModelOutputMapper,
                model_client: Gr00tModelClient) -> tuple[ModelPort, ActionPort]:
        """Create model and action adapters with given mapper and client."""
        image_handler = ImageHandler(self.config.image_features)
        joint_state_handler = JointStateHandler(self.config.robot_configs)
        robots = self._create_robots()
        model_input_mapper = Gr00tInputMapper(self.config.robot_configs, self.config.image_features)
        model_adapter = Gr00tAdapter(model_client, model_input_mapper, model_output_mapper, [image_handler, joint_state_handler])
        action_adapter = FollowJointTrajectoryAdapter(robots, joint_state_handler)

        return (model_adapter, action_adapter)

    def create_default(self) -> tuple[ModelPort, ActionPort]:
        """Create adapters with default joint state mapper."""
        model_output_mapper = Gr00tJointStateMapper(self.config.robot_configs)
        return self._create(model_output_mapper, Gr00tClient(self.config))

    def create_rtc(self) -> tuple[ModelPort, ActionPort]:
        """Create adapters with real-time control joint state mapper."""
        model_output_mapper = Gr00tJointStateMapperRTC(self.config.robot_configs)
        return self._create(model_output_mapper, Gr00tClient(self.config))

    def create_rtc_constant(self) -> tuple[ModelPort, ActionPort]:
        """Create adapters with RTC mapper and constant test client."""
        model_output_mapper = Gr00tJointStateMapperRTC(self.config.robot_configs)
        return self._create(model_output_mapper, ConstantGr00tRTCClient(self.config))

    def create_so101_constant_dual(self) -> tuple[ModelPort, ActionPort]:
        """Create adapters with RTC mapper and constant dual-arm test client."""
        model_output_mapper = Gr00tJointStateMapperRTC(self.config.robot_configs)
        return self._create(model_output_mapper, ConstantDualGr00tClient(self.config))

