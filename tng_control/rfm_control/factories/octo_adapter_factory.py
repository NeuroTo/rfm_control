from tng_control.rfm_control.observation_handler.joint_state_handler import JointStateHandler
from tng_control.rfm_control.observation_handler.image_handler import ImageHandler
from tng_control.rfm_control.action_adapter.robot import Robot
from tng_control.rfm_control.model_adapter.model_clients.octo.octo_client import OctoClient
from tng_control.rfm_control.config.model_configs.octo_config import OctoConfig
from tng_control.rfm_control.model_adapter.mapper.input.octo_input_mapper import OctoInputMapper
from tng_control.rfm_control.model_adapter.mapper.output.delta_endeffector_mapper import OctoDeltaEndeffectorMapper
from tng_control.rfm_control.action_adapter.action_port import ActionPort
from tng_control.rfm_control.action_adapter.follow_joint_trajectory_adapter import FollowJointTrajectoryAdapter
from tng_control.rfm_control.action_adapter.mapper.delta_endeffector_action_mapper import DeltaEndeffectorActionMapper
from tng_control.action_executor.joint_trajectory_action_executor import JointTrajectoryActionExecutor
from tng_control.action_executor.gripper_action_executor import GripperActionExecutor
from tng_control.rfm_control.model_adapter.octo_adapter import OctoAdapter
from tng_control.rfm_control.model_adapter.model_port import ModelPort
from tng_control.rfm_control.model_adapter.model_clients.octo.octo_model_client import OctoModelClient
from tng_control.test.model_adapter.model_clients.constant_octo_client import ConstantOctoClient


class OctoAdapterFactory:
    """
    Factory for creating Octo model and action adapters.
    
    Octo uses delta endeffector actions, so all configurations use
    DeltaEndeffectorActionMapper for action mapping.
    """

    def __init__(self, config: OctoConfig):
        self.config = config

    def _create(self, model_client: OctoModelClient) -> tuple[ModelPort, ActionPort]:
        """Create model and action adapters with given client."""
        image_handler = ImageHandler(self.config.image_features)
        joint_state_handler = JointStateHandler(self.config.robot_configs)
        model_input_mapper = OctoInputMapper(self.config.robot_configs, self.config.image_features)
        model_output_mapper = OctoDeltaEndeffectorMapper(self.config.robot_configs)
        model_adapter = OctoAdapter(model_client, model_input_mapper, model_output_mapper, [image_handler])
        robots = [
            Robot(
                prefix=robot_config.prefix,
                action_mapper=DeltaEndeffectorActionMapper(robot_config),
                arm_action_executor=JointTrajectoryActionExecutor(robot_config.arm_keys.topic_name),
                gripper_action_executor=GripperActionExecutor(robot_config.gripper_keys.topic_name)
            )
            for robot_config in self.config.robot_configs
        ]
        action_adapter = FollowJointTrajectoryAdapter(robots, joint_state_handler)
        return (model_adapter, action_adapter)

    def create_default(self) -> tuple[ModelPort, ActionPort]:
        """Create adapters with default Octo client."""
        model_client = OctoClient(self.config)
        return self._create(model_client)

    def create_constant_client(self) -> tuple[ModelPort, ActionPort]:
        """Create adapters with constant test client."""
        model_client = ConstantOctoClient()
        return self._create(model_client)

