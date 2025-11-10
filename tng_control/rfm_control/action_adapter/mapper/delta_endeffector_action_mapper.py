from typing_extensions import override

from sensor_msgs.msg import JointState
from geometry_msgs.msg import Pose, PoseStamped
from moveit_msgs.msg import RobotState
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from tng_octo.fk_solver import MoveitFKSolver
from tng_octo.ik_solver import MoveitIKSolver
from tng_control.rfm_control.action_adapter.mapper.pose_util import add_pose
from tng_control.rfm_control.model_adapter.mapper.pose_util import action_to_pose
from tng_control.rfm_control.action_adapter.mapper.action_mapper import ActionMapper
from tng_control.rfm_control.domain_model.arm_action import ArmAction
from tng_control.rfm_control.domain_model.delta_endeffector_action import DeltaEndeffectorAction
from tng_control.rfm_control.config.model_configs.robot_config import RobotConfig

duration_between_goals: Duration = Duration(sec=0, nanosec=10**8)


class DeltaEndeffectorActionMapper(ActionMapper[JointTrajectory]):
    """
    Stateful mapper for delta endeffector actions.
    Requires current joint state to compute forward and inverse kinematics.
    """

    def __init__(self, robot_config: RobotConfig) -> None:
        self.joint_names = robot_config.arm_keys.joint_names
        self.fk_solver: MoveitFKSolver = MoveitFKSolver(
            ["tool0"], robot_config.arm_keys.joint_names)
        self.ik_solver: MoveitIKSolver = MoveitIKSolver(
            robot_config.group_name, robot_config.frame_id, robot_config.arm_keys.joint_names)

    @override
    def map_action_to_executor_input(
            self, 
            action: ArmAction, 
            state: JointState | None = None
    ) -> JointTrajectory:
        """
        Map delta endeffector action to JointTrajectory using IK.
        
        Args:
            action: Must be a DeltaEndeffectorAction
            state: Current joint state (required for FK/IK computation)
            
        Returns:
            JointTrajectory with a single point containing the IK solution
            
        Raises:
            ValueError: If action is not a DeltaEndeffectorAction or if state is None
            RuntimeError: If IK or FK fails to find a solution
        """
        if not isinstance(action, DeltaEndeffectorAction):
            raise ValueError("Action must be an instance of DeltaEndeffectorAction")
        
        if state is None:
            raise ValueError("DeltaEndeffectorActionMapper requires current joint state for IK computation")

        action_pose: Pose = action_to_pose(action.position, action.orientation)
        current_robot_state: RobotState = RobotState()
        current_robot_state.joint_state = state

        fk_output: list[PoseStamped] | None = self.fk_solver.get_pose(current_robot_state)
        if fk_output is None:
            raise RuntimeError(f"Forward kinematics failed to compute current pose for robot_state: {current_robot_state}")
        current_pose: PoseStamped = fk_output[0]

        target_pose: Pose = add_pose(current_pose.pose, action_pose)

        point: JointTrajectoryPoint | None = self._solve_inverse_kinematic(
            pose=target_pose, 
            seed_robot_state=current_robot_state,
            duration=Duration(
                sec=int(action.time_between_goals),
                nanosec=int((action.time_between_goals % 1) * 1e9)
            )
        )
        
        if point is None:
            raise RuntimeError(f"Inverse kinematics failed to find solution for target pose: {target_pose}")

        return JointTrajectory(
            joint_names=self.joint_names,
            points=[point]
        )


    def _solve_inverse_kinematic(
            self, pose: Pose, seed_robot_state: RobotState | None = None,
            duration: Duration = duration_between_goals) -> JointTrajectoryPoint | None:
        return self.ik_solver.get_joint_positions_from_pose(
            pose=pose, duration=duration, seed_robot_state=seed_robot_state, ik_link_name="tool0")

