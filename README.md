# RFM Control

ROS2 package for robot control using foundation models (Robot Foundation Model Control).

## Package Contents

This package provides infrastructure for controlling robots using AI foundation models like GR00T and Octo:

This package contains:
- Configuration-driven architecture based on Hexagonal Architecture (Ports and Adapters pattern)
- Support for multiple AI models (GR00T, Octo) and robots
- YAML-based configuration for flexible robot setups
- Type-safe configuration with Pydantic validation
- Action execution components for robot controllers (joint trajectory, gripper control)

## Quick Start

### Installation

```bash
# Build the ROS2 package
cd /path/to/workspace
colcon build --packages-select rfm_control

# Source the workspace
source install/setup.bash
```

### Using Action Executors Independently

The `action_executor` module can be used independently from the RFM control system. Action executors provide a simple, type-safe interface to execute robot commands via ROS2 actions.

#### Available Executors

- **`JointTrajectoryActionExecutor`**: Execute joint trajectories via `FollowJointTrajectory` action
- **`GripperActionExecutor`**: Control grippers via `GripperCommand` action
- **`JointTrajectoryTopicExecutor`**: Publish joint trajectories directly to topics (no action server)

#### Example: Direct Joint Trajectory Execution

```python
import rclpy
from rclpy.node import Node
from rfm_control.action_executor.joint_trajectory_action_executor import JointTrajectoryActionExecutor
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# Initialize ROS2
rclpy.init()
node = Node('my_robot_controller')

# Create executor for your robot's controller
executor = JointTrajectoryActionExecutor('/arm_controller/follow_joint_trajectory')

# Create a trajectory command
trajectory = JointTrajectory()
trajectory.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']

point = JointTrajectoryPoint()
point.positions = [0.0, -1.57, 1.57, 0.0, 0.0, 0.0]
point.time_from_start.sec = 2
trajectory.points.append(point)

# Execute asynchronously
future = executor.execute_async(trajectory, node)

# Wait for completion
rclpy.spin_until_future_complete(node, future)

if future.result():
    print("Trajectory executed successfully!")
else:
    print("Trajectory execution failed")

node.destroy_node()
rclpy.shutdown()
```

#### Example: Gripper Control

```python
from rfm_control.action_executor.gripper_action_executor import GripperActionExecutor
from control_msgs.msg import GripperCommand

# Create gripper executor
gripper_executor = GripperActionExecutor('/gripper_controller/gripper_cmd')

# Create gripper command
gripper_command = GripperCommand()
gripper_command.position = 0.8  # Open to 80%
gripper_command.max_effort = 50.0

# Execute
future = gripper_executor.execute_async(gripper_command, node)
rclpy.spin_until_future_complete(node, future)
```

#### Use Cases for Independent Usage

- **Manual robot control scripts**: Direct scripting of robot motions
- **Testing and debugging**: Test robot controllers without full RFM setup
- **Simple automation tasks**: Lightweight automation without AI models
- **Integration with other systems**: Use action executors in custom control loops

### Use RFM Control with Configuration

```bash
# Run RFM action server with a configuration file
ros2 run rfm_control rfm_action_server path/to/config.yaml

# Example: Run with GR00T mock configuration
ros2 run rfm_control rfm_action_server \
  src/rfm_control/rfm_control/config/configs/gr00t_mock.yaml
```

### Python API

```python
from rfm_control.factories.adapter_factory import AdapterFactory
from rfm_control.rfm_action_server import RfmActionServer

# Load configuration and create adapters
factory = AdapterFactory()
model_port, action_port = factory.create_adapters("config/gr00t_so101.yaml")

# Initialize and run server
server = RfmActionServer(model_port, action_port)
server.move_from_prompt("pick up the cup")
```

## Documentation

For detailed documentation about rfm control, configuration guides, and extension examples, see:

📘 **[RFM Control Documentation](src/rfm_control/README.md)**

This includes:
- **Architecture Overview**: Hexagonal Architecture, layers, and execution flow
- **Configuration Guide**: Step-by-step guide to configure for your robot
- **Extension Guide**: How to add new models, action mappers, and transformations
- **Example Configurations**: Pre-configured setups for various robots and models

## Configuration Files

Example configurations are available in [`src/rfm_control/rfm_control/config/configs/`](src/rfm_control/rfm_control/config/configs/):

| Configuration | Description |
|---------------|-------------|
| `gr00t_mock.yaml` | GR00T model with mock client (testing) |
| `gr00t_so101_rtc.yaml` | GR00T model with SO-101 robot (real-time control) |
| `gr00t_so101_dual.yaml` | GR00T model with dual-arm setup |
| `octo_ur5_mock.yaml` | Octo model with UR5 robot (mock client) |
