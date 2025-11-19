import pytest
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, HistoryPolicy, DurabilityPolicy
from std_msgs.msg import String
from pathlib import Path

from shared.robot_description_listener import get_robot_description_from_topic
from shared.ros2_control_joint_config import Ros2ControlJointConfig, parse_robot_description_to_joint_configs


class RobotDescriptionPublisher(Node):
    """Dummy publisher for robot description topic."""
    
    def __init__(self, robot_description_content: str):
        super().__init__('robot_description_publisher')
        self.publisher = self.create_publisher(
            String,
            'robot_description',
            QoSProfile(
                depth=1,
                history=HistoryPolicy.KEEP_LAST,
                durability=DurabilityPolicy.TRANSIENT_LOCAL
            )
        )
        
        # Publish the robot description
        msg = String()
        msg.data = robot_description_content
        self.publisher.publish(msg)
        self.get_logger().info('Published robot description')


@pytest.fixture(scope="module")
def ros2_context():
    """Initialize ROS2 for all tests in this module."""
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def robot_description_content():
    """Load the robot description from the test file."""
    test_dir = Path(__file__).parent
    robot_description_file = test_dir / "dummy_robot_description.xml"
    
    assert robot_description_file.exists(), f"Robot description file not found: {robot_description_file}"
    
    with open(robot_description_file, 'r') as f:
        content = f.read()
    
    return content


def test_get_and_parse_robot_description(ros2_context, robot_description_content):
    """Test getting robot description from topic and parsing it to joint configs."""
    
    # Create the publisher
    publisher_node = RobotDescriptionPublisher(robot_description_content)
    
    # Spin once to ensure message is published
    rclpy.spin_once(publisher_node, timeout_sec=0.1)
    
    # Small delay to ensure publisher is ready
    time.sleep(0.1)
    
    try:
        # Get robot description from topic
        robot_description: str = get_robot_description_from_topic()
        
        assert robot_description is not None, "Robot description should not be None"
        assert len(robot_description) > 0, "Robot description should not be empty"
        
        print(f"\nRobot description length: {len(robot_description)} characters")
        
        # Parse to joint configs
        joint_configs: list[Ros2ControlJointConfig] = parse_robot_description_to_joint_configs(robot_description)
        
        assert joint_configs is not None, "Joint configs should not be None"
        assert len(joint_configs) > 0, "Should have at least one joint config"
        
        print(f"Found {len(joint_configs)} joint configs")
        for config in joint_configs:
            print(f"  - Prefix: {config.prefix}")
            print(f"    Arm joints: {config.arm_joint_names}")
            print(f"    Gripper joint: {config.gripper_joint_name}")
    
    finally:
        publisher_node.destroy_node()