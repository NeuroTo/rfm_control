"""Configuration schema for robot foundation model control using Pydantic."""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self

from rfm_control.config.config_types import (
    ModelType,
    ClientType,
    MapperType,
    ActionType,
    ActionMapperType,
    ImageType,
    TransformationType,
)


class ArmConfig(BaseModel):
    """Configuration for arm (or gripper) motion control."""
    
    topic_name: str = Field(
        ..., 
        description="ROS2 topic name for trajectory execution",
        examples=["/arm_controller/follow_joint_trajectory"]
    )
    model_input_position_key: str = Field(
        ..., 
        description="Dictionary key for position data sent to model",
        examples=["state.single_arm", "state.joint_positions"]
    )
    model_input_velocity_key: str = Field(
        "", 
        description="Dictionary key for velocity data sent to model (optional)"
    )
    model_input_load_key: str = Field(
        "", 
        description="Dictionary key for load/effort data sent to model (optional)"
    )
    model_output_position_key: str = Field(
        ..., 
        description="Dictionary key for position data received from model",
        examples=["action.single_arm", "action.joint_positions"]
    )
    model_output_velocity_key: str = Field(
        "", 
        description="Dictionary key for velocity data received from model (optional)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "topic_name": "/arm_controller/follow_joint_trajectory",
                "model_input_position_key": "state.single_arm",
                "model_input_velocity_key": "",
                "model_input_load_key": "",
                "model_output_position_key": "action.single_arm",
                "model_output_velocity_key": ""
            }]
        }
    }


class RobotConfigYaml(BaseModel):
    """Robot configuration from YAML."""
    
    prefix: str = Field(
        ..., 
        description="Robot identifier prefix (empty string for single robot)",
        examples=["", "right_arm", "left_arm"]
    )
    group_name: str = Field(
        ..., 
        description="MoveIt planning group name for IK and FK solver (optional)",
        examples=["arm", "manipulator"]
    )
    frame_id: str = Field(
        ..., 
        description="Reference frame for the robot",
        examples=["world", "base_link"]
    )
    joint_state_topic: str = Field(
        ..., 
        description="ROS2 topic for joint state subscription",
        examples=["/joint_states"]
    )
    time_between_goals: float = Field(
        default=0.5,
        ge=0.0,
        description="Time interval between trajectory waypoints in seconds"
    )
    arm: ArmConfig = Field(..., description="Arm motion configuration")
    gripper: ArmConfig = Field(..., description="Gripper motion configuration")


class ImageConfigYaml(BaseModel):
    """Image configuration from YAML."""
    
    model_input_key: str = Field(
        ..., 
        description="Dictionary key for image data sent to model",
        examples=["video.wrist", "image_primary"]
    )
    topic_name: str = Field(
        ..., 
        description="ROS2 topic for image subscription",
        examples=["/wrist/image_raw/compressed", "/camera/rgb/image_raw"]
    )
    resolution: tuple[int, int] = Field(
        ..., 
        description="Target image resolution as [width, height]",
        examples=[(640, 480), (256, 256)]
    )
    image_type: ImageType = Field(
        default="compressed",
        description="ROS2 image message type"
    )
    transformation: TransformationType = Field(
        default="identity",
        description="Model-specific image transformation"
    )
    
    @field_validator('resolution', mode='before')
    @classmethod
    def validate_resolution(cls, v):
        """Convert list to tuple for resolution."""
        if isinstance(v, list):
            if len(v) != 2:
                raise ValueError("Resolution must have exactly 2 values [width, height]")
            return tuple(v)
        return v


class ModelConfigYaml(BaseModel):
    """Model configuration from YAML."""
    
    type: ModelType = Field(
        ..., 
        description="Type of robot foundation model"
    )
    mapper_type: MapperType = Field(
        default="default",
        description="Output mapper variant (model-specific)"
    )
    client_type: ClientType = Field(
        default="real",
        description="Model client type (real model or mock test values)"
    )
    port: int = Field(
        default=8043,
        ge=1,
        le=65535,
        description="Model server port number"
    )


class ActionConfigYaml(BaseModel):
    """Action adapter configuration from YAML."""
    
    type: ActionType = Field(
        default="follow_joint_trajectory",
        description="Type of action adapter/controller"
    )
    arm_action_mapper: ActionMapperType = Field(
        default="absolute_joint",
        description="Action mapper type for arm actions (must match model output type)"
    )


class RfmConfigYaml(BaseModel):
    """Complete RFM control configuration from YAML."""
    
    model: ModelConfigYaml = Field(..., description="Model configuration")
    action: ActionConfigYaml = Field(
        default_factory=ActionConfigYaml,
        description="Action adapter configuration"
    )
    robots: list[RobotConfigYaml] = Field(
        ..., 
        min_length=1,
        description="List of robot configurations (at least one required)"
    )
    images: list[ImageConfigYaml] = Field(
        default_factory=list,
        description="List of image/camera configurations"
    )
    
    @model_validator(mode='after')
    def validate_robot_prefixes(self) -> Self:
        """Ensure robot prefixes are unique."""
        prefixes = [robot.prefix for robot in self.robots]
        if len(prefixes) != len(set(prefixes)):
            raise ValueError("Robot prefixes must be unique")
        return self

