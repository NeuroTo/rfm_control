from typing import Callable
from attr import dataclass
import numpy as np

from sensor_msgs.msg import Image, CompressedImage


@dataclass
class ImageFeature():

    model_input_image_key: str
    resolution: tuple[int, int]
    topic_name: str
    transformation: Callable[[np.ndarray], np.ndarray] = lambda x: x
    image_type: type = CompressedImage
