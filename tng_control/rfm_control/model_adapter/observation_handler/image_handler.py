from collections.abc import Sequence
import numpy as np
from cv_bridge import CvBridge
import cv2
from sensor_msgs.msg import Image, CompressedImage
import rclpy
from rclpy.subscription import Subscription
from rclpy.node import Node
from tng_control.rfm_control.model_adapter.observation_handler.observation_handler import ObservationHandler
from tng_control.rfm_control.model_adapter.observation_handler.image_feature import ImageFeature
from tng_control.rfm_control.rfm_control_status_code import ImageNotAvailableException


class ImageHandler(ObservationHandler):

    subscription_images: Sequence[Subscription] | None = None

    def __init__(self, image_features: Sequence[ImageFeature]) -> None:
        self.image_features = image_features
        self.current_images: dict[str, Image | CompressedImage] = {}
        self.cv2_bridge: CvBridge = CvBridge()

    def create_subscription(self, node: Node) -> None:
        if self.subscription_images is not None:
            return
        qos_profile = rclpy.qos.QoSProfile(
            reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT,
            history=rclpy.qos.HistoryPolicy.KEEP_LAST, depth=1)
        self.subscription_images = [
            node.create_subscription(
                image_feature.image_type, image_feature.topic_name, lambda x,
                key=image_feature.topic_name: self._update_callback(x, key),
                qos_profile=qos_profile)
            for image_feature in self.image_features
        ]

    def get_observation_dict(self) -> dict[str, np.ndarray]:
        observation = {}
        for image_ft in self.image_features:
            if image_ft.topic_name not in self.current_images:
                raise ImageNotAvailableException(image_ft.topic_name)
            observation[image_ft.model_input_image_key] = self._process_image(image_ft)
        return observation

    def _process_image(self, image_ft: ImageFeature) -> np.ndarray:
        image = self.current_images[image_ft.topic_name]
        encoded_image = self._decode_ros_image(image)
        resized_image = cv2.resize(encoded_image, image_ft.resolution)
        return image_ft.transformation(resized_image)

    def _decode_ros_image(self, image: Image | CompressedImage) -> np.ndarray:
        if isinstance(image, Image):
            return np.array(self.cv2_bridge.imgmsg_to_cv2(image, desired_encoding='bgr8'))
        if isinstance(image, CompressedImage):
            return np.array(self.cv2_bridge.compressed_imgmsg_to_cv2(
                image, desired_encoding='bgr8'))
        raise TypeError(f"Unsupported image type: {type(image)}")

    def _update_callback(self, image: Image | CompressedImage, key: str) -> None:
        self.current_images[key] = image
