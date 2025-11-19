from pathlib import Path

from tng_control.action_adapter.action_port import ActionPort
from tng_control.model_adapter.model_port import ModelPort
from tng_control.factories.adapter_factory import AdapterFactory


class AdapterProvider:
    """
    Provider for creating model and action adapters from YAML configuration.
    
    Loads robot foundation model configurations from YAML files and creates
    appropriate adapters for model inference and action execution.
    
    Example usage:
        provider = AdapterProvider()
        model_port, action_port = provider.get_adapters("config/configs/gr00t_so101.yaml")
    """

    def get_adapters(self, config_path: str | Path) -> tuple[ModelPort, ActionPort]:
        """
        Get adapters from YAML configuration file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Tuple of (ModelPort, ActionPort) configured from YAML

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid

        Example:
            >>> provider = AdapterProvider()
            >>> model_port, action_port = provider.get_adapters(
            ...     "config/configs/gr00t_so101.yaml"
            ... )
        """
        factory = AdapterFactory()
        return factory.create_adapters(config_path)
