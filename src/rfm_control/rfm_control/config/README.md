# RFM Control YAML Configuration

This directory contains YAML configuration files for robot foundation model control.

> 📘 **Note**: All YAML files are validated using [Pydantic](https://docs.pydantic.dev/) for type safety.  
> See [`SCHEMA_VALIDATION.md`](../SCHEMA_VALIDATION.md) for details on validation, schema generation, and IDE integration.

## ✅ Validation

All configurations are automatically validated when loaded. To manually validate:

```bash
# Validate a single file
python -m rfm_control.config.validate_yaml gr00t_so101.yaml

# Validate all configs
python -m rfm_control.config.validate_yaml -d .
```

## Quick Start

### Using YAML Configuration

```python
from rfm_control.adapter_provider import AdapterProvider

# Load configuration from YAML
provider = AdapterProvider()
model_port, action_port = provider.get_adapters(
    "config/configs/gr00t_so101.yaml"
)
```

### ROS2 Launch

```bash
ros2 run rfm_control rfm_action_server config/configs/gr00t_so101.yaml
```

## Configuration File Structure

### Basic Structure

```yaml
model:
  type: gr00t  # or octo
  mapper_type: default  # or rtc
  client_type: real  # or mock
  port: 8043

action:
  type: follow_joint_trajectory  # Currently only supported type
  arm_action_mapper: absolute_joint  # 'absolute_joint' or 'delta_endeffector'

robots:
  - prefix: ""
    group_name: "arm"
    frame_id: "world"
    joint_state_topic: "/joint_states"
    time_between_goals: 0.5
    arm: ...
    gripper: ...

images:
  - model_input_key: "video.wrist"
    topic_name: "/camera/image/compressed"
    resolution: [224, 224]
    image_type: compressed  # or raw
    transformation: gr00t  # identity, gr00t, or octo
```

## Client Types

- **`real`**: Connect to actual model server
- **`mock`**: Use mock test client (for testing)

## Image Configuration

### Image Types
- **`raw`**: `sensor_msgs/Image`
- **`compressed`**: `sensor_msgs/CompressedImage`

### Transformation Types
- **`identity`**: No transformation (pass through)
- **`gr00t`**: `np.array([np.array([x])])`
- **`octo`**: `np.array([np.array([x])])`

## Example Configurations

### GR00T SO-101 (Dual Arm)

See `gr00t_so101.yaml` for a complete dual-arm configuration with:
- Left and right arm controllers
- Dual wrist cameras
- RTC-compatible mapper

### Octo UR5 (Single Arm)

See `octo_ur5.yaml` for a single-arm configuration with:
- UR5 arm controller
- Single camera
- Delta endeffector actions

## Creating Custom Configurations

1. **Copy an existing config** as a template:
   ```bash
   cp gr00t_so101.yaml my_robot.yaml
   ```

2. **Modify robot settings**:
   - Update `prefix` for each robot
   - Set correct topic names for controllers
   - Adjust `model_input_*_key` and `model_output_*_key` to match your model

3. **Configure cameras**:
   - Set `topic_name` to your camera topics
   - Adjust `resolution` for your model
   - Choose appropriate `transformation`

4. **Set model parameters**:
   - Choose `mapper_type` based on your needs
   - Set `port` to match your model server

5. **Test configuration**:
   ```python
   factory = AdapterFactory("path/to/my_robot.yaml")
   model_port, action_port = factory.create_adapters()
   ```


## Troubleshooting

### FileNotFoundError
- Check that config file path is correct
- Use absolute path or path relative to working directory

### ValueError: No ROS2 config found
- Ensure robot `prefix` matches ROS2 control configuration
- Check that robot description is published on `/robot_description`

### KeyError in YAML
- Verify all required fields are present
- Check YAML syntax (indentation, colons, hyphens)

### Unknown model type
- Ensure `model.type` is either `gr00t` or `octo`
- Check spelling and case (lowercase only)

---

## 🚀 Complete Guide: Configuring for Your Robot

This section provides a step-by-step guide to create a configuration for your specific robot setup.

### Prerequisites

Before creating a configuration, gather the following information:

- **Robot Information**:
  - ROS2 controller topic names (arm and gripper)
  - Joint state topic name
  - MoveIt planning group name
  - Number of joints (arm and gripper)
  
- **Camera Information**:
  - Camera topic names
  - Image types (raw or compressed)
  - Desired resolution for model input
  
- **Model Information**:
  - Model type (GR00T or Octo)
  - Model server port
  - Input/output key format (check model documentation)

### Step-by-Step Configuration

#### 1. Choose a Template

Start with the configuration that most closely matches your setup:

| Template | Use Case |
|----------|----------|
| `gr00t_mock.yaml` | Single arm, GR00T model, testing without model server |
| `gr00t_so101_rtc.yaml` | Single arm, GR00T model, real-time control |
| `gr00t_so101_dual.yaml` | Dual arm setup, GR00T model |
| `octo_ur5_mock.yaml` | Single arm, Octo model, testing |

```bash
cd rfm_control/config/configs/
cp gr00t_mock.yaml my_robot_config.yaml
```

#### 2. Configure Model Settings

```yaml
model:
  type: gr00t              # Options: 'gr00t' or 'octo'
  mapper_type: default     # Options: 'default' or 'rtc' (GR00T only)
  client_type: mock        # Options: 'real', 'mock', 'mock_rtc' (GR00T only)
  port: 8043               # Model server port (if client_type: real)
```

**Key Decisions**:
- Use `client_type: mock` for testing without a model server
- Use `mapper_type: rtc` for single-step GR00T outputs (real-time control)
- Use `mapper_type: default` for trajectory-based GR00T outputs

#### 3. Configure Action Adapter

```yaml
action:
  type: follow_joint_trajectory  # Currently only supported type
  arm_action_mapper: absolute_joint  # Options: 'absolute_joint' or 'delta_endeffector'
```

**Key Decisions**:
- Use `absolute_joint` for GR00T models (outputs absolute joint positions)
- Use `delta_endeffector` for Octo models (outputs delta endeffector poses)

#### 4. Configure Robot(s)

For each robot in your setup:

```yaml
action:
  type: follow_joint_trajectory
  arm_action_mapper: absolute_joint  # Must match model output type

robots:
  - prefix: ""                          # Empty for single robot, "left_arm"/"right_arm" for dual
    group_name: "arm"                   # MoveIt planning group name
    frame_id: "world"                   # Reference frame
    joint_state_topic: "/joint_states"  # Where to read joint states
    time_between_goals: 0.5             # Time between trajectory waypoints (seconds)
    
    arm:
      topic_name: "/arm_controller/follow_joint_trajectory"
      model_input_position_key: "state.single_arm"    # Key in model input dict
      model_input_velocity_key: ""                    # Optional
      model_input_load_key: ""                        # Optional
      model_output_position_key: "action.single_arm"  # Key in model output dict
      model_output_velocity_key: ""                   # Optional
    
    gripper:
      topic_name: "/gripper_controller/gripper_cmd"
      model_input_position_key: "state.gripper"
      model_input_velocity_key: ""
      model_input_load_key: ""
      model_output_position_key: "action.gripper"
      model_output_velocity_key: ""
```

**Important**:
- `topic_name`: Must match your ROS2 controller name
- `model_input_*_key`: Must match what your model expects (check model documentation)
- `model_output_*_key`: Must match what your model outputs
- For dual-arm setups, add a second robot entry with a different `prefix`

#### 5. Configure Camera(s)

For each camera:

```yaml
images:
  - model_input_key: "video.wrist"                     # Key in model input dict
    topic_name: "/wrist/image_raw/compressed"          # ROS2 camera topic
    resolution: [640, 480]                             # Target resolution [width, height]
    image_type: compressed                             # 'raw' or 'compressed'
    transformation: gr00t                              # 'identity', 'gr00t', or 'octo'
```

**Key Decisions**:
- `image_type`: Use `compressed` for better network performance, `raw` for local cameras
- `resolution`: Must match model's expected input size (e.g., GR00T: [640, 480], Octo: [256, 256])
- `transformation`: Use model-specific transformation (`gr00t` or `octo`) or `identity` for no transformation

#### 6. Validate Configuration

```bash
# Validate your configuration
python -m rfm_control.config.validate_yaml my_robot_config.yaml
```

Fix any validation errors before proceeding.

#### 7. Test Configuration

Create a simple test script:

```python
from rfm_control.factories.adapter_factory import AdapterFactory

# Load your configuration
factory = AdapterFactory()
try:
    model_port, action_port = factory.create_adapters("path/to/my_robot_config.yaml")
    print("✅ Configuration loaded successfully!")
except Exception as e:
    print(f"❌ Configuration error: {e}")
```

#### 8. Test with Mock Client

Before connecting to a real robot or model server, test with mock clients:

```yaml
model:
  client_type: mock  # Uses mock client (no model server needed)
```

This allows you to verify:
- ROS2 topics are correctly configured
- Camera topics are publishing
- Joint state topic is available
- Action executors can connect to controllers

### Real-World Example: Configuring a New UR5 Robot

Let's say you have a UR5 robot with:
- Arm controller: `/ur5_arm_controller/follow_joint_trajectory`
- Gripper controller: `/robotiq_gripper_controller/gripper_cmd`
- Joint states: `/joint_states`
- Wrist camera: `/camera/image_raw/compressed`
- External camera: `/external_camera/image_raw`

**Step 1**: Copy template
```bash
cp gr00t_mock.yaml my_ur5_config.yaml
```

**Step 2**: Update action and robot configuration
```yaml
action:
  type: follow_joint_trajectory
  arm_action_mapper: absolute_joint  # GR00T outputs absolute joint positions

robots:
  - prefix: ""
    group_name: "manipulator"  # UR5 MoveIt group name
    frame_id: "base_link"
    joint_state_topic: "/joint_states"
    time_between_goals: 0.5
    
    arm:
      topic_name: "/ur5_arm_controller/follow_joint_trajectory"
      model_input_position_key: "state.joint_positions"
      model_input_velocity_key: ""
      model_input_load_key: ""
      model_output_position_key: "action.joint_positions"
      model_output_velocity_key: ""
    
    gripper:
      topic_name: "/robotiq_gripper_controller/gripper_cmd"
      model_input_position_key: "state.gripper_position"
      model_input_velocity_key: ""
      model_input_load_key: ""
      model_output_position_key: "action.gripper_position"
      model_output_velocity_key: ""
```

**Step 3**: Update camera configuration
```yaml
images:
  - model_input_key: "video.wrist_cam"
    topic_name: "/camera/image_raw/compressed"
    resolution: [640, 480]
    image_type: compressed
    transformation: gr00t

  - model_input_key: "video.external_cam"
    topic_name: "/external_camera/image_raw"
    resolution: [640, 480]
    image_type: raw  # Not compressed
    transformation: gr00t
```

**Step 4**: Validate and test
```bash
python -m rfm_control.config.validate_yaml my_ur5_config.yaml
```

### Common Patterns

#### Pattern 1: Dual Arm Setup

```yaml
robots:
  - prefix: "left_arm"
    # ... left arm configuration
    
  - prefix: "right_arm"
    # ... right arm configuration
```

**Note**: Ensure `prefix` values are unique!

#### Pattern 2: Multiple Cameras

```yaml
images:
  - model_input_key: "video.wrist"
    # ... wrist camera config
    
  - model_input_key: "video.global_front"
    # ... front camera config
    
  - model_input_key: "video.global_side"
    # ... side camera config
```

#### Pattern 3: Testing → Production

**Testing (my_robot_test.yaml)**:
```yaml
model:
  client_type: mock  # No model server needed
```

**Production (my_robot_prod.yaml)**:
```yaml
model:
  client_type: real  # Connect to model server
  port: 8043
```

Same configuration, just change `client_type`!

### Next Steps

Once your configuration is working:

1. **Add to version control**: Commit your YAML file
2. **Create launch file**: Create a ROS2 launch file that uses your config
3. **Document specifics**: Add comments in your YAML file for team members
4. **Test thoroughly**: Test with mock clients before connecting to real hardware

---

## 🔧 Extending the Configuration System

This section explains how to extend the system with new components while maintaining the configuration-driven architecture.

### Adding a New Model

To add support for a new AI model (e.g., "RT-1", "OpenVLA"):

#### 1. Define Configuration Type

Add the new model type to [`config_types.py`](../config_types.py):

```python
# Model Types
MODEL_TYPE_GR00T = "gr00t"
MODEL_TYPE_OCTO = "octo"
MODEL_TYPE_RT1 = "rt1"  # ← NEW

ModelType = Literal[MODEL_TYPE_GR00T, MODEL_TYPE_OCTO, MODEL_TYPE_RT1]
MODEL_TYPES: Tuple[ModelType, ...] = (MODEL_TYPE_GR00T, MODEL_TYPE_OCTO, MODEL_TYPE_RT1)
```

#### 2. Implement Model Components

Create the following components for your model:

**a) Model Client** (`model_clients/rt1/rt1_client.py`):
```python
from rfm_control.model_adapter.model_clients.model_client import ModelClient

class RT1Client(ModelClient[RT1Action]):
    """Client for RT-1 model server."""
    
    def get_action(self, observation: dict, prompt: str) -> RT1Action:
        # Implement communication with RT-1 model server
        response = self._call_rt1_server(observation, prompt)
        return RT1Action(response)
```

**b) Model Input Mapper** (`mapper/input/rt1_input_mapper.py`):
```python
from rfm_control.model_adapter.mapper.input.model_input_mapper import ModelInputMapper

class RT1InputMapper(ModelInputMapper):
    """Maps generic observations to RT-1 input format."""
    
    def transform_observation(self, obs: Observations) -> dict:
        # Transform observations to RT-1's expected format
        return {
            "image": self._transform_images(obs.images),
            "state": self._transform_joint_states(obs.joint_states),
            "instruction": obs.prompt
        }
```

**c) Model Output Mapper** (`mapper/output/rt1_output_mapper.py`):
```python
from rfm_control.model_adapter.mapper.output.model_output_mapper import ModelOutputMapper

class RT1OutputMapper(ModelOutputMapper):
    """Maps RT-1 output to robot actions."""
    
    def to_action(self, model_output: RT1Action) -> list[RobotAction]:
        # Transform RT-1 output to RobotAction format
        return [self._create_robot_action(robot, model_output) 
                for robot in self.robot_configs]
```

**d) Model Adapter** (`rt1_adapter.py`):
```python
from rfm_control.model_adapter.model_port import ModelPort

class RT1Adapter(ModelPort):
    """Adapter for RT-1 model."""
    
    def __init__(
        self,
        model_client: RT1Client,
        input_mapper: RT1InputMapper,
        output_mapper: RT1OutputMapper,
        observation_handlers: list[ObservationHandler]
    ):
        # Initialize adapter
        ...
```

#### 3. Register in Model Factories

**a) Create Model Client Factory** (`factories/rt1_model_client_factory.py`):
```python
from rfm_control.config.config_types import CLIENT_TYPE_REAL, CLIENT_TYPE_MOCK

class RT1ModelClientFactory:
    def __init__(self):
        self._registry = {
            CLIENT_TYPE_REAL: self._create_real_client,
            CLIENT_TYPE_MOCK: self._create_mock_client,
        }
    
    def create(self, client_type: str, model_config) -> RT1Client:
        factory_method = self._registry.get(client_type)
        if factory_method is None:
            raise ValueError(f"Unknown RT-1 client type: '{client_type}'")
        return factory_method(model_config)
```

**b) Register in ModelAdapterFactory** (`factories/model_adapter_factory.py`):
```python
from rfm_control.config.config_types import MODEL_TYPE_RT1

class ModelAdapterFactory:
    def __init__(self, ..., rt1_client_factory=None, rt1_output_mapper_factory=None):
        # Inject RT-1 factories
        self.rt1_client_factory = rt1_client_factory or RT1ModelClientFactory()
        self.rt1_output_mapper_factory = rt1_output_mapper_factory or RT1ModelOutputMapperFactory()
        
        # Register RT-1 adapter
        self._registry = {
            MODEL_TYPE_GR00T: self._create_gr00t_adapter,
            MODEL_TYPE_OCTO: self._create_octo_adapter,
            MODEL_TYPE_RT1: self._create_rt1_adapter,  # ← NEW
        }
    
    def _create_rt1_adapter(self, yaml_config, robot_configs, image_configs, ...):
        # Create RT-1 adapter
        input_mapper = RT1InputMapper(robot_configs, image_configs)
        output_mapper = self.rt1_output_mapper_factory.create(
            yaml_config.model.mapper_type, robot_configs
        )
        model_client = self.rt1_client_factory.create(
            yaml_config.model.client_type, model_config
        )
        return RT1Adapter(model_client, input_mapper, output_mapper, [...])
```

#### 4. Update Configuration Schema

Update [`config_schema.py`](../config_schema.py) if you need model-specific fields:

```python
from rfm_control.config.config_types import ModelType

class ModelConfigYaml(BaseModel):
    type: ModelType = Field(..., description="Type of robot foundation model")
    # ... existing fields
    
    # Optional: Add model-specific fields with validators
    rt1_specific_param: str | None = Field(
        None, 
        description="RT-1 specific parameter (only for RT-1 model)"
    )
```

#### 5. Create YAML Configuration

Create a new configuration file (`configs/rt1_ur5.yaml`):

```yaml
model:
  type: rt1
  mapper_type: default
  client_type: real
  port: 9000

action:
  type: follow_joint_trajectory
  arm_action_mapper: absolute_joint  # or delta_endeffector, depending on RT-1 output

robots:
  - prefix: ""
    group_name: "arm"
    # ... robot configuration

images:
  - model_input_key: "image"
    # ... image configuration
```

#### 6. Test Your Implementation

```python
from rfm_control.factories.adapter_factory import AdapterFactory

# Load your new configuration
factory = AdapterFactory()
model_port, action_port = factory.create_adapters("config/configs/rt1_ur5.yaml")

# Test with mock client first
# Then test with real model server
```

### Adding a New Action Mapper

To add a new action mapper (e.g., for Cartesian control):

#### 1. Define Action Mapper Type

Add to [`config_types.py`](../config_types.py):

```python
ACTION_MAPPER_TYPE_ABSOLUTE_JOINT = "absolute_joint"
ACTION_MAPPER_TYPE_DELTA_ENDEFFECTOR = "delta_endeffector"
ACTION_MAPPER_TYPE_CARTESIAN = "cartesian"  # ← NEW

ActionMapperType = Literal[
    ACTION_MAPPER_TYPE_ABSOLUTE_JOINT,
    ACTION_MAPPER_TYPE_DELTA_ENDEFFECTOR,
    ACTION_MAPPER_TYPE_CARTESIAN,
]
```

#### 2. Implement Action Mapper

Create `action_adapter/mapper/cartesian_action_mapper.py`:

```python
from rfm_control.action_adapter.mapper.action_mapper import ActionMapper
from trajectory_msgs.msg import JointTrajectory

class CartesianActionMapper(ActionMapper[JointTrajectory]):
    """Maps Cartesian pose commands to joint trajectories."""
    
    def map_action_to_executor_input(
        self, 
        action: RobotAction, 
        current_state: JointState
    ) -> JointTrajectory:
        # Use IK to convert Cartesian pose to joint positions
        target_joints = self._compute_ik(action.cartesian_pose)
        return self._create_trajectory(target_joints)
```

#### 3. Register in ActionMapperFactory

Update [`factories/action_mapper_factory.py`](../../factories/action_mapper_factory.py):

```python
from rfm_control.config.config_types import ACTION_MAPPER_TYPE_CARTESIAN

class ActionMapperFactory:
    def __init__(self):
        self._registry = {
            ACTION_MAPPER_TYPE_ABSOLUTE_JOINT: self._create_absolute_joint_mapper,
            ACTION_MAPPER_TYPE_DELTA_ENDEFFECTOR: self._create_delta_endeffector_mapper,
            ACTION_MAPPER_TYPE_CARTESIAN: self._create_cartesian_mapper,  # ← NEW
        }
    
    def _create_cartesian_mapper(self, robot_config):
        return CartesianActionMapper(robot_config)
```

#### 4. Update Configuration

Use in your YAML:

```yaml
action:
  type: follow_joint_trajectory
  arm_action_mapper: cartesian  # ← NEW
```

### Adding Custom Image Transformations

To add a new image transformation:

#### 1. Define Transformation Type

Add to [`config_types.py`](../config_types.py):

```python
TRANSFORMATION_TYPE_IDENTITY = "identity"
TRANSFORMATION_TYPE_GR00T = "gr00t"
TRANSFORMATION_TYPE_OCTO = "octo"
TRANSFORMATION_TYPE_CUSTOM = "custom"  # ← NEW
```

#### 2. Implement Transformation

In your model input mapper:

```python
def _apply_transformation(self, image: np.ndarray, transformation: str) -> np.ndarray:
    if transformation == "custom":
        # Apply your custom transformation
        return self._custom_transform(image)
    # ... existing transformations
```

#### 3. Use in Configuration

```yaml
images:
  - model_input_key: "video.wrist"
    topic_name: "/camera/image_raw"
    resolution: [256, 256]
    transformation: custom  # ← NEW
```

### Extension Checklist

When adding a new component, ensure you:

- [ ] Define constants in `config_types.py`
- [ ] Update `Literal` types in `config_types.py`
- [ ] Implement the component (client, mapper, adapter)
- [ ] Create a factory for the component
- [ ] Register the factory in the appropriate registry
- [ ] Update `config_schema.py` if needed (for validation)
- [ ] Create example YAML configurations
- [ ] Add tests for your component
- [ ] Update documentation

### Design Principles for Extensions

1. **Follow Hexagonal Architecture**: 
   - Implement interfaces (Ports) for your components
   - Keep adapters independent of external frameworks

2. **Use Dependency Injection**:
   - Inject dependencies through constructors
   - Make factories configurable

3. **Maintain Configuration-Driven Design**:
   - All behavior changes should be possible through YAML
   - No code changes required for different setups

4. **Keep Type Safety**:
   - Use `Literal` types for configuration values
   - Validate with Pydantic

5. **Follow the Registry Pattern**:
   - Use dictionaries to map string identifiers to factory methods
   - Makes the system easily extensible

### Getting Help

- Check existing configurations in `configs/` for examples
- See [`config_schema.py`](../config_schema.py) for full schema definition
- Review [`config_types.py`](../config_types.py) for all valid type values
- Look at existing factories in `factories/` for patterns
- Run validation to get detailed error messages

