"""Factory for creating model adapters."""
from typing import Callable

from tng_control.rfm_control.config.config_types import MODEL_TYPE_GR00T, MODEL_TYPE_OCTO, MAPPER_TYPE_DEFAULT
from tng_control.rfm_control.model_adapter.gr00t_adapter import Gr00tAdapter
from tng_control.rfm_control.model_adapter.mapper.input.gr00t_input_mapper import Gr00tInputMapper
from tng_control.rfm_control.model_adapter.mapper.input.octo_input_mapper import OctoInputMapper
from tng_control.rfm_control.model_adapter.model_port import ModelPort
from tng_control.rfm_control.config.config_schema import RfmConfigYaml
from tng_control.rfm_control.config.config_models.robot_config import RobotConfig
from tng_control.rfm_control.config.config_models.image_config import ImageConfig
from tng_control.rfm_control.model_adapter.octo_adapter import OctoAdapter
from tng_control.rfm_control.observation_handler.image_handler import ImageHandler
from tng_control.rfm_control.observation_handler.joint_state_handler import JointStateHandler

# Import model-specific factories directly
from tng_control.rfm_control.factories.gr00t_model_client_factory import Gr00tModelClientFactory
from tng_control.rfm_control.factories.octo_model_client_factory import OctoModelClientFactory
from tng_control.rfm_control.factories.gr00t_model_output_mapper_factory import Gr00tModelOutputMapperFactory
from tng_control.rfm_control.factories.octo_model_output_mapper_factory import OctoModelOutputMapperFactory


ModelAdapterFactoryMethod = Callable[
    [RfmConfigYaml, list[RobotConfig], list[ImageConfig], ImageHandler, JointStateHandler],
    ModelPort
]


class ModelAdapterFactory:
    """
    Factory for creating model adapters.
    
    Creates ModelPort instances based on model type string.
    """
    
    def __init__(
        self,
        gr00t_client_factory: Gr00tModelClientFactory | None = None,
        octo_client_factory: OctoModelClientFactory | None = None,
        gr00t_output_mapper_factory: Gr00tModelOutputMapperFactory | None = None,
        octo_output_mapper_factory: OctoModelOutputMapperFactory | None = None
    ):
        """
        Initialize model adapter factory with model-specific sub-factories.
        
        Args:
            gr00t_client_factory: Factory for creating GR00T clients
            octo_client_factory: Factory for creating Octo clients
            gr00t_output_mapper_factory: Factory for creating GR00T output mappers
            octo_output_mapper_factory: Factory for creating Octo output mappers
        """
        # Model-specific factories
        self.gr00t_client_factory = gr00t_client_factory or Gr00tModelClientFactory()
        self.octo_client_factory = octo_client_factory or OctoModelClientFactory()
        self.gr00t_output_mapper_factory = gr00t_output_mapper_factory or Gr00tModelOutputMapperFactory()
        self.octo_output_mapper_factory = octo_output_mapper_factory or OctoModelOutputMapperFactory()
        
        self._registry: dict[str, ModelAdapterFactoryMethod] = {
            MODEL_TYPE_GR00T: self._create_gr00t_adapter,
            MODEL_TYPE_OCTO: self._create_octo_adapter,
        }
    
    def create(
        self,
        model_type: str,
        yaml_config: RfmConfigYaml,
        robot_configs: list[RobotConfig],
        image_configs: list[ImageConfig],
        image_handler: ImageHandler,
        joint_state_handler: JointStateHandler
    ) -> ModelPort:
        """
        Create model adapter based on type.
        
        Args:
            model_type: Type of model adapter
            yaml_config: Complete YAML configuration
            robot_configs: Robot configurations
            image_configs: Image configurations
            image_handler: Image observation handler
            joint_state_handler: Joint state observation handler
            
        Returns:
            ModelPort instance
            
        Raises:
            ValueError: If model_type is not registered
        """
        factory_method = self._registry.get(model_type)
        
        if factory_method is None:
            raise ValueError(
                f"Unknown model type: '{model_type}'. "
                f"Supported types: {list(self._registry.keys())}"
            )
        
        return factory_method(
            yaml_config, robot_configs, image_configs, image_handler, joint_state_handler
        )


    def _create_gr00t_adapter(self, yaml_config: RfmConfigYaml, robot_configs: list[RobotConfig], image_configs: list[ImageConfig], image_handler: ImageHandler, joint_state_handler: JointStateHandler) -> ModelPort:
        """Create GR00T model adapter."""
        # Import base class
        from tng_control.rfm_control.config.model_client_config_base import Gr00tConfigBase
        
        # Create config implementation for GR00T client
        class Gr00tConfigFromYaml(Gr00tConfigBase):
            """Config implementation for YAML-based GR00T configuration."""
            def __init__(self, port: int):
                self._port = port
            
            @property
            def port(self) -> int:
                return self._port
        
        model_config = Gr00tConfigFromYaml(yaml_config.model.port)
        
        # Create mappers using GR00T-specific factories
        input_mapper = Gr00tInputMapper(robot_configs, image_configs)
        output_mapper = self.gr00t_output_mapper_factory.create(
            yaml_config.model.mapper_type,
            robot_configs
        )
        
        # Create client using GR00T-specific factory
        model_client = self.gr00t_client_factory.create(
            yaml_config.model.client_type,
            model_config
        )
        
        return Gr00tAdapter(
            model_client,
            input_mapper,
            output_mapper,
            [image_handler, joint_state_handler]
        )
        
    def _create_octo_adapter(self, yaml_config: RfmConfigYaml, robot_configs: list[RobotConfig], image_configs: list[ImageConfig], image_handler: ImageHandler, joint_state_handler: JointStateHandler) -> ModelPort:
        """Create Octo model adapter."""
        # Import base class
        from tng_control.rfm_control.config.model_client_config_base import OctoConfigBase
        
        # Create config implementation for Octo client
        class OctoConfigFromYaml(OctoConfigBase):
            """Config implementation for YAML-based Octo configuration."""
            @property
            def model_path(self) -> str:
                return "hf://rail-berkeley/octo-small-1.5"
            
            def get_dataset_statistics(self, model):
                return model.dataset_statistics["berkeley_autolab_ur5"]["action"]
        
        model_config = OctoConfigFromYaml()
        
        # Create mappers using Octo-specific factories
        input_mapper = OctoInputMapper(robot_configs, image_configs)
        output_mapper = self.octo_output_mapper_factory.create(
            MAPPER_TYPE_DEFAULT,
            robot_configs
        )
        
        # Create client using Octo-specific factory
        model_client = self.octo_client_factory.create(
            yaml_config.model.client_type,
            model_config
        )
        
        return OctoAdapter(
            model_client,
            input_mapper,
            output_mapper,
            [image_handler, joint_state_handler]
        )
     
    @property
    def supported_types(self) -> list[str]:
        """Get list of supported model types."""
        return list(self._registry.keys())


