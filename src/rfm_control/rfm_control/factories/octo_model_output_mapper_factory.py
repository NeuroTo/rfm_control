from typing import Callable

from rfm_control.config.config_types import MAPPER_TYPE_DEFAULT
from rfm_control.model_adapter.mapper.output.delta_endeffector_mapper import OctoDeltaEndeffectorMapper
from rfm_control.model_adapter.mapper.output.model_output_mapper import ModelOutputMapper
from rfm_control.config.config_models.robot_config import RobotConfig


class OctoModelOutputMapperFactory:
    """
    Factory for creating Octo output mappers.
    
    Creates Octo ModelOutputMapper instances (currently only delta endeffector).
    """
    
    def __init__(self):
        self._registry: dict[str, Callable[[list[RobotConfig]], ModelOutputMapper]] = {
            MAPPER_TYPE_DEFAULT: self._create_delta_endeffector_mapper,
        }
    
    def create(self, mapper_type: str, robot_configs: list[RobotConfig]) -> ModelOutputMapper:
        """
        Create Octo output mapper based on mapper type.
        
        Args:
            mapper_type: Type of mapper ('default')
            robot_configs: Robot configurations
            
        Returns:
            ModelOutputMapper instance
            
        Raises:
            ValueError: If mapper_type is not supported
        """
        factory_method = self._registry.get(mapper_type)
        if factory_method is None:
            raise ValueError(
                f"Unknown Octo mapper type: '{mapper_type}'. "
                f"Supported types: {list(self._registry.keys())}"
            )
        
        return factory_method(robot_configs)
    
    def _create_delta_endeffector_mapper(self, robot_configs: list[RobotConfig]) -> ModelOutputMapper:
        """Create Octo delta endeffector mapper."""
        return OctoDeltaEndeffectorMapper(robot_configs)
    
    @property
    def supported_types(self) -> list[str]:
        """Get list of supported mapper types."""
        return list(self._registry.keys())


