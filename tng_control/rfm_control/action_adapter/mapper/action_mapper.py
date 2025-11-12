from abc import ABC, abstractmethod
from typing import Generic

from sensor_msgs.msg import JointState

from tng_control.rfm_control.domain_model.arm_action import ArmAction
from tng_control.action_executor.motion_executor import CommandType


class ActionMapper(ABC, Generic[CommandType]):
    """
    Abstract base class for mapping actions to executor-specific command types.
    
    The CommandType parameter matches the input type expected by the associated
    MotionExecutor (e.g., JointTrajectory for FollowJointTrajectory controller).
    
    Mappers can be stateless (e.g., direct joint position mapping) or stateful
    (e.g., IK-based mapping that requires current joint state).
    """

    @abstractmethod
    def map_action_to_executor_input(
            self, 
            action: ArmAction, 
            state: JointState | None = None
    ) -> CommandType:
        """
        Map an action to the executor-specific command type.
        
        Args:
            action: The action to map
            state: Current joint state (required for stateful mappers like IK-based mappers,
                   optional for stateless mappers)
        
        Returns:
            The executor command (e.g., JointTrajectory for FollowJointTrajectory controller)
            
        Raises:
            ValueError: If state is required but None is provided
        """
        pass
