"""Factory for creating GR00T model output mappers."""
from typing import Callable

from tng_control.config.config_types import MAPPER_TYPE_DEFAULT, MAPPER_TYPE_RTC
from tng_control.model_adapter.mapper.output.joint_state_mapper import Gr00tJointStateMapper, Gr00tJointStateMapperRTC
from tng_control.model_adapter.mapper.output.model_output_mapper import ModelOutputMapper
from tng_control.config.config_models.robot_config import RobotConfig


class Gr00tModelOutputMapperFactory:
    """
    Factory for creating GR00T output mappers.
    
    Creates GR00T ModelOutputMapper instances based on mapper type.
    """
    
    def __init__(self):
        self._registry: dict[str, Callable[[list[RobotConfig]], ModelOutputMapper]] = {
            MAPPER_TYPE_DEFAULT: self._create_default_mapper,
            MAPPER_TYPE_RTC: self._create_rtc_mapper,
        }
    
    def create(self, mapper_type: str, robot_configs: list[RobotConfig]) -> ModelOutputMapper:
        """
        Create GR00T output mapper based on mapper type.
        
        Args:
            mapper_type: Type of mapper ('default', 'rtc')
            robot_configs: Robot configurations
            
        Returns:
            ModelOutputMapper instance
            
        Raises:
            ValueError: If mapper_type is not supported
        """
        factory_method = self._registry.get(mapper_type)
        if factory_method is None:
            raise ValueError(
                f"Unknown GR00T mapper type: '{mapper_type}'. "
                f"Supported types: {list(self._registry.keys())}"
            )
        
        return factory_method(robot_configs)
    
    def _create_default_mapper(self, robot_configs: list[RobotConfig]) -> ModelOutputMapper:
        """Create GR00T joint state mapper (default)."""
        return Gr00tJointStateMapper(robot_configs)
    
    def _create_rtc_mapper(self, robot_configs: list[RobotConfig]) -> ModelOutputMapper:
        """Create GR00T joint state mapper (RTC variant)."""
        return Gr00tJointStateMapperRTC(robot_configs)
    
    @property
    def supported_types(self) -> list[str]:
        """Get list of supported mapper types."""
        return list(self._registry.keys())


