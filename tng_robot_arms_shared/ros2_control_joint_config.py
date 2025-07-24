
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from tng_robot_arms_shared.robot_model_config import RobotModelConfig

@dataclass
class Ros2ControlJointConfig:
    prefix: str
    arm_joints: list[str]
    """names of the arm joints. Each joint name should start with the given prefix."""
    gripper_joint: str
    """names of the gripper joint. Should start with the given prefix."""

def parse_robot_description_to_joint_configs(robot_description: str, prefixes: list[str] | None = None) -> list[Ros2ControlJointConfig]:
    root = ET.fromstring(robot_description)

    # Find the <ros2_control> block (may be multiple)
    ros2_control_nodes = root.findall(".//ros2_control")
    if not ros2_control_nodes:
        raise ValueError("No <ros2_control> elements found in the URDF.")

    # joint names controlled by ros2_control. mimic joints are excluded.
    controlled_joints = [j.attrib["name"] 
                            for node in ros2_control_nodes 
                            for j in node.findall(".//joint") 
                            if not any(p.attrib.get("name") == "mimic" for p in j.findall("param"))]

    joint_configs: list[Ros2ControlJointConfig] = []

    if prefixes is None:
        prefixes = RobotModelConfig.instance().prefixes

    for prefix in prefixes:
        if prefix == '':
            # empty prefixed joints are joints that do NOT start with any other known prefix
            other_prefixes = [p for p in prefixes if p != '']
            prefixed_joints = [j for j in controlled_joints if not any(j.startswith(p) for p in other_prefixes)]
        else:
            prefixed_joints = [j for j in controlled_joints if j.startswith(prefix)]
        if not prefixed_joints or len(prefixed_joints) == 0:
            raise ValueError(f"No joints found for prefix '{prefix}'")

        # Find the gripper joint
        gripper_candidates = [j for j in prefixed_joints if 'gripper' in j or 'hand' in j or 'finger' in j]
        if not gripper_candidates or len(gripper_candidates) != 1:
            raise ValueError(f"No unique gripper joint found for prefix '{prefix}'. Found {gripper_candidates}")

        gripper_joint = gripper_candidates[0]
        arm_joints = [j for j in prefixed_joints if j != gripper_joint]

        joint_configs.append(Ros2ControlJointConfig(prefix, arm_joints, gripper_joint))
    
    return joint_configs
