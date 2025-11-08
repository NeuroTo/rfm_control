from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectoryPoint

from typing_extensions import override

from tng_octo.fk_solver import MoveitFKSolver
from tng_control.action_adapter.mapper.action_mapper import ActionMapper
from tng_control.domain_model.absolute_joint_state_action import AbsoluteJointStateAction
from tng_control.domain_model.arm_action import ArmAction


class AbsoluteJointActionMapper(ActionMapper):
    _fk_solver: MoveitFKSolver | None = None

    def __init__(self, joint_names: list[str], fk_solver=None):
        self.joint_names = joint_names
        self._fk_solver = fk_solver

    @override
    def action_to_joint_trajectory_point(
            self, action: ArmAction, state: JointState) -> JointTrajectoryPoint:
        if not isinstance(action, AbsoluteJointStateAction):
            raise ValueError("Action must be an instance of AbsoluteJointStateAction")
        point = JointTrajectoryPoint()
        point.positions = [float(x) for x in action.joint_states]
        return point
