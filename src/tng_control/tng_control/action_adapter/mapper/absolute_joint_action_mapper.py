from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

from typing_extensions import override

from tng_control.action_adapter.mapper.action_mapper import ActionMapper
from tng_control.domain_model.absolute_joint_state_action import AbsoluteJointStateAction
from tng_control.domain_model.arm_action import ArmAction


class AbsoluteJointActionMapper(ActionMapper[JointTrajectory]):
    """
    Stateless mapper for absolute joint position actions.
    Maps joint positions directly without requiring current state.
    """
    
    def __init__(self, joint_names: list[str]):
        self.joint_names = joint_names

    @override
    def map_action_to_executor_input(
            self, 
            action: ArmAction, 
            state: JointState | None = None
    ) -> JointTrajectory:
        """
        Map absolute joint action to JointTrajectory.
        
        Args:
            action: Must be an AbsoluteJointStateAction
            state: Not used by this stateless mapper
            
        Returns:
            JointTrajectory with a single point containing the target joint positions
            
        Raises:
            ValueError: If action is not an AbsoluteJointStateAction
        """
        if not isinstance(action, AbsoluteJointStateAction):
            raise ValueError("Action must be an instance of AbsoluteJointStateAction")
        
        point = JointTrajectoryPoint()
        point.positions = [float(x) for x in action.joint_states]
        point.time_from_start = Duration(
            sec=int(action.time_between_goals),
            nanosec=int((action.time_between_goals % 1) * 1e9)
        )
        
        return JointTrajectory(
            joint_names=self.joint_names,
            points=[point]
        )

