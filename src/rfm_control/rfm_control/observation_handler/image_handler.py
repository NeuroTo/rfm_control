from collections.abc import Sequence
from typing_extensions import override
import numpy as np
from cv_bridge import CvBridge

from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from rclpy.subscription import Subscription
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage

from rfm_control.observation_handler.observation_handler import ObservationHandler
from rfm_control.config.config_models.image_config import ImageConfig
from rfm_control.observation_handler.observation_dto import Observations
from rfm_control.exceptions import ImageNotAvailableException


class ImageHandler(ObservationHandler):

    subscription_images: Sequence[Subscription] | None = None

    def __init__(self, image_configs: Sequence[ImageConfig]) -> None:
        self.image_configs = image_configs
        self.current_images: dict[str, Image | CompressedImage] = {}
        self.cv2_bridge: CvBridge = CvBridge()

    @override
    def create_subscription(self, node: Node) -> None:
        if self.subscription_images is not None:
            return
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST, depth=1)
        
        # Create subscriptions with proper callback binding
        subscriptions = []
        for image_config in self.image_configs:
            def make_callback(topic_name):
                return lambda msg: self._update_callback(msg, key=topic_name)
            
            subscription = node.create_subscription(
                image_config.image_type,
                image_config.topic_name,
                make_callback(image_config.topic_name),
                qos_profile=qos_profile)
            subscriptions.append(subscription)
        
        self.subscription_images = subscriptions

    @override
    def get_observations(self) -> Observations:
        """
        Get image observations.
        
        Returns a partial Observations object with images populated.
        Robots field uses default (empty list).
        """
        images = {}
        for image_config in self.image_configs:
            if image_config.topic_name not in self.current_images:
                raise ImageNotAvailableException(image_config.topic_name)
            # Store raw decoded image without resizing or model-specific transformation
            images[image_config.topic_name] = self._decode_ros_image(
                self.current_images[image_config.topic_name]
            )
        return Observations(images=images)

    def _decode_ros_image(self, image: Image | CompressedImage) -> np.ndarray:
        if isinstance(image, Image):
            return np.array(self.cv2_bridge.imgmsg_to_cv2(image, desired_encoding='bgr8'))
        if isinstance(image, CompressedImage):
            return np.array(self.cv2_bridge.compressed_imgmsg_to_cv2(
                image, desired_encoding='bgr8'))
        raise TypeError(f"Unsupported image type: {type(image)}")

    def _update_callback(self, image: Image | CompressedImage, key: str) -> None:
        self.current_images[key] = image

