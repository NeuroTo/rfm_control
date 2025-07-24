import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, HistoryPolicy, DurabilityPolicy
from std_msgs.msg import String

class RobotDescriptionListener(Node):
    def __init__(self):
        super().__init__('robot_description_listener')

        self.get_logger().log("Waiting for data on 'robot_description' topic to finish initialization")
        
        self.robot_description = None

        self.robot_description_subscription = self.create_subscription(
            String,
            'robot_description',
            self.robot_description_callback,
            QoSProfile(
                depth=1,
                history=HistoryPolicy.KEEP_LAST, 
                durability=DurabilityPolicy.TRANSIENT_LOCAL)
        )

    def robot_description_callback(self, msg: String):
        self.get_logger().info('Received robot description')
        self.robot_description = msg.data
        self.destroy_node()

def get_robot_description_from_topic() -> str:
    """
    Returns the robot_description from the '/robot_description' topic.  
    Assumes that rclpy.init() has already been called.
    """
    listener = RobotDescriptionListener()
    rclpy.spin_once(listener)
    if listener.robot_description is None:
        raise RuntimeError("No robot_description received")
    return listener.robot_description
