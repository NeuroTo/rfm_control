from dataclasses import dataclass


# TODO: make this configurable
DEFAULT_TIME_BETWEEN_GOALS: float = 0.5

@dataclass
class RobotOutputKeys():
    topic_name: str
    joint_names: list[str]
    input_position_key: str
    input_velocity_key: str
    input_load_key: str
    output_position_key: str
    output_velocity_key: str


@dataclass
class RobotConfig:
    prefix: str
    group_name: str
    frame_id: str
    arm_keys: RobotOutputKeys
    gripper_keys: RobotOutputKeys
    time_between_goals: float = DEFAULT_TIME_BETWEEN_GOALS
