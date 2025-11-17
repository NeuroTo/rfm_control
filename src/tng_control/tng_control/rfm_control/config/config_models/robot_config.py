from dataclasses import dataclass


# TODO: make this configurable
DEFAULT_TIME_BETWEEN_GOALS: float = 0.5

@dataclass
class ActuatorConfig():
    topic_name: str
    joint_names: list[str]
    model_input_position_key: str
    model_input_velocity_key: str
    model_input_load_key: str
    model_output_position_key: str
    model_output_velocity_key: str


@dataclass
class RobotConfig:
    prefix: str
    group_name: str
    frame_id: str
    arm_config: ActuatorConfig
    gripper_config: ActuatorConfig
    joint_state_topic: str
    time_between_goals: float = DEFAULT_TIME_BETWEEN_GOALS

