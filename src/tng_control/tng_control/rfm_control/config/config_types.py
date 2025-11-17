"""
Central type definitions and constants for RFM control configuration.

This module provides a single source of truth for all configuration keys and types
used across factories and configuration schemas.
"""
from typing import Literal, get_args


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL TYPES
# ═══════════════════════════════════════════════════════════════════════════════

MODEL_TYPE_GR00T = "gr00t"
MODEL_TYPE_OCTO = "octo"

ModelType = Literal["gr00t", "octo"]
MODEL_TYPES: tuple[str, ...] = get_args(ModelType)


# ═══════════════════════════════════════════════════════════════════════════════
# CLIENT TYPES
# ═══════════════════════════════════════════════════════════════════════════════

CLIENT_TYPE_REAL = "real"
CLIENT_TYPE_MOCK = "mock"
CLIENT_TYPE_MOCK_RTC = "mock_rtc"

ClientType = Literal["real", "mock", "mock_rtc"]
CLIENT_TYPES: tuple[str, ...] = get_args(ClientType)


# ═══════════════════════════════════════════════════════════════════════════════
# MAPPER TYPES (Model Output Mappers)
# ═══════════════════════════════════════════════════════════════════════════════

MAPPER_TYPE_DEFAULT = "default"
MAPPER_TYPE_RTC = "rtc"

MapperType = Literal["default", "rtc"]
MAPPER_TYPES: tuple[str, ...] = get_args(MapperType)


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION TYPES (Action Adapters)
# ═══════════════════════════════════════════════════════════════════════════════

ACTION_TYPE_FOLLOW_JOINT_TRAJECTORY = "follow_joint_trajectory"
ACTION_TYPE_CARTESIAN_CONTROL = "cartesian_control"
ACTION_TYPE_FEED_FORWARD = "feed_forward"

ActionType = Literal["follow_joint_trajectory", "cartesian_control", "feed_forward"]
ACTION_TYPES: tuple[str, ...] = get_args(ActionType)


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION MAPPER TYPES
# ═══════════════════════════════════════════════════════════════════════════════

ACTION_MAPPER_TYPE_ABSOLUTE_JOINT = "absolute_joint"
ACTION_MAPPER_TYPE_DELTA_ENDEFFECTOR = "delta_endeffector"

ActionMapperType = Literal["absolute_joint", "delta_endeffector"]
ACTION_MAPPER_TYPES: tuple[str, ...] = get_args(ActionMapperType)


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

IMAGE_TYPE_RAW = "raw"
IMAGE_TYPE_COMPRESSED = "compressed"

ImageType = Literal["raw", "compressed"]
IMAGE_TYPES: tuple[str, ...] = get_args(ImageType)


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSFORMATION TYPES
# ═══════════════════════════════════════════════════════════════════════════════

TRANSFORMATION_TYPE_IDENTITY = "identity"
TRANSFORMATION_TYPE_GR00T = "gr00t"
TRANSFORMATION_TYPE_OCTO = "octo"

TransformationType = Literal["identity", "gr00t", "octo"]
TRANSFORMATION_TYPES: tuple[str, ...] = get_args(TransformationType)

