from enum import Enum


class RfmControlStatusCode(Enum):
    SUCCESS = 0
    FAILURE = 1
    ACTION_MAPPING_FAILED = 2               # Action
    ROBOT_ACTION_EXECUTION_FAILED = 3       # Action
    INFERENCE_FAILED = 4                    # Model
    IMAGES_UNAVAILABLE = 5                  # Model
    JOINTS_STATES_UNAVAILABLE = 6           # Model
    GRIPPER_ACTION_EXECUTION_FAILED = 7     # Action
