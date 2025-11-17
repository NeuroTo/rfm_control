from typing import Callable

from tng_control.rfm_control.config.config_types import CLIENT_TYPE_REAL, CLIENT_TYPE_MOCK, CLIENT_TYPE_MOCK_RTC
from tng_control.rfm_control.config.model_client_config_base import Gr00tConfigBase
from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_client import Gr00tClient
from tng_control.rfm_control.model_adapter.model_clients.gr00t.gr00t_model_client import Gr00tModelClient
from tng_control.test.model_adapter.model_clients.gr00t_client_mock import Gr00tClientMock, Gr00tRTCClientMock


class Gr00tModelClientFactory:
    """
    Factory for creating GR00T model clients.
    
    Creates GR00T ModelClient instances based on client type (real vs mock variants).
    """
    
    def __init__(self):
        self._registry: dict[str, Callable[[Gr00tConfigBase | None], Gr00tModelClient]] = {
            CLIENT_TYPE_REAL: self._create_real_client,
            CLIENT_TYPE_MOCK: self._create_mock_client,
            CLIENT_TYPE_MOCK_RTC: self._create_mock_rtc_client,
        }
    
    def create(self, client_type: str, model_config: Gr00tConfigBase | None) -> Gr00tModelClient:
        """
        Create GR00T model client based on client type.
        
        Args:
            client_type: Type of client ('real', 'mock')
            model_config: GR00T model configuration
            
        Returns:
            Gr00tModelClient instance
            
        Raises:
            ValueError: If client_type is not supported
        """
        factory_method = self._registry.get(client_type)
        if factory_method is None:
            raise ValueError(
                f"Unknown GR00T client type: '{client_type}'. "
                f"Supported types: {list(self._registry.keys())}"
            )
        
        return factory_method(model_config)
    
    def _create_real_client(self, model_config: Gr00tConfigBase | None) -> Gr00tModelClient:
        """Create real GR00T client."""
        if model_config is None:
            raise ValueError("Model configuration is required for real GR00T client.")
        return Gr00tClient(model_config)
    
    def _create_mock_client(self, model_config: Gr00tConfigBase | None) -> Gr00tModelClient:
        """Create standard mock GR00T client (cycles through joint positions)."""
        return Gr00tClientMock()
    
    def _create_mock_rtc_client(self, model_config: Gr00tConfigBase | None) -> Gr00tModelClient:
        """Create RTC mock GR00T client (uses RTC action format)."""
        return Gr00tRTCClientMock()
    
    @property
    def supported_types(self) -> list[str]:
        """Get list of supported client types."""
        return list(self._registry.keys())


