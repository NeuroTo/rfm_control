from tng_control.config.model_configs.gr00t_config import Gr00tSO101Config, Gr00tSo101DualArmConfig
from tng_control.rfm_control.model_adapter.observation_handler.image_feature import ImageFeature


class ConstGr00tSo101DualArmConfig(Gr00tSo101DualArmConfig):
    @property
    def image_features(self) -> list[ImageFeature]:
        return []


class ConstGr00t(Gr00tSO101Config):
    @property
    def image_features(self) -> list[ImageFeature]:
        return []
