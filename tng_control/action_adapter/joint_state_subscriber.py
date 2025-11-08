from sensor_msgs.msg import JointState
from rclpy.node import Node
from rclpy.subscription import Subscription

from tng_control.rfm_control.exceptions import JointStatesNotAvailableException


class JointStateSubscriber:
    """
    Simple joint state subscriber.
    """

    joint_state_subscriber: Subscription | None = None

    def __init__(self, topic_name: str) -> None:
        self.joint_state_topic = topic_name
        self._current_joint_state: JointState | None = None

    def create_subscription(self, node: Node) -> None:
        """Create ROS2 subscription to joint state topic."""
        if self.joint_state_subscriber is not None:
            return
        self.joint_state_subscriber = node.create_subscription(
            JointState,
            self.joint_state_topic,
            self._update_callback,
            10)

    def get_current_joint_state(self) -> JointState:
        """Get the current joint state."""
        if not self._current_joint_state:
            raise JointStatesNotAvailableException()
        return self._current_joint_state

    def _update_callback(self, joint_state: JointState) -> None:
        """Callback for joint state updates."""
        self._current_joint_state = joint_state

