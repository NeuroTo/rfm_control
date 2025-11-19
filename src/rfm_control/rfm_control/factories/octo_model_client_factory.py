from typing import Callable

from rfm_control.config.config_types import CLIENT_TYPE_REAL, CLIENT_TYPE_MOCK
from rfm_control.config.model_client_config_base import OctoConfigBase
from rfm_control.model_adapter.model_clients.octo.octo_client import OctoClient
from rfm_control.model_adapter.model_clients.octo.octo_model_client import OctoModelClient
from rfm_control.test.model_adapter.model_clients.octo_client_mock import OctoClientMock


class OctoModelClientFactory:
    """
    Factory for creating Octo model clients.
    
    Creates Octo ModelClient instances based on client type (real vs mock).
    """
    
    def __init__(self):
        self._registry: dict[str, Callable[[OctoConfigBase | None], OctoModelClient]] = {
            CLIENT_TYPE_REAL: self._create_real_client,
            CLIENT_TYPE_MOCK: self._create_mock_client,
        }
    
    def create(self, client_type: str, model_config: OctoConfigBase | None = None) -> OctoModelClient:
        """
        Create Octo model client based on client type.
        
        Args:
            client_type: Type of client ('real', 'mock')
            model_config: Octo model configuration (optional for mock)
            
        Returns:
            OctoModelClient instance
            
        Raises:
            ValueError: If client_type is not supported
        """
        factory_method = self._registry.get(client_type)
        if factory_method is None:
            raise ValueError(
                f"Unknown Octo client type: '{client_type}'. "
                f"Supported types: {list(self._registry.keys())}"
            )
        
        return factory_method(model_config)
    
    def _create_real_client(self, model_config: OctoConfigBase | None) -> OctoModelClient:
        """Create real Octo client."""
        if model_config is None:
            raise ValueError("Model configuration is required for real Octo client.")
        return OctoClient(model_config)
    
    def _create_mock_client(self, model_config: OctoConfigBase | None) -> OctoModelClient:
        """Create mock Octo client (doesn't need config)."""
        return OctoClientMock()
    
    @property
    def supported_types(self) -> list[str]:
        """Get list of supported client types."""
        return list(self._registry.keys())


