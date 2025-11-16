# RFM Control YAML Configuration

This directory contains YAML configuration files for robot foundation model control.

> 📘 **Note**: All YAML files are validated using [Pydantic](https://docs.pydantic.dev/) for type safety.  
> See [`SCHEMA_VALIDATION.md`](../SCHEMA_VALIDATION.md) for details on validation, schema generation, and IDE integration.

## ✅ Validation

All configurations are automatically validated when loaded. To manually validate:

```bash
# Validate a single file
python -m tng_control.rfm_control.config.validate_yaml gr00t_so101.yaml

# Validate all configs
python -m tng_control.rfm_control.config.validate_yaml -d .
```

## Quick Start

### Using YAML Configuration

```python
from tng_control.rfm_control.adapter_provider import AdapterProvider

# Load configuration from YAML
provider = AdapterProvider()
model_port, action_port = provider.get_adapters(
    "config/configs/gr00t_so101.yaml"
)
```

### ROS2 Launch

```bash
ros2 run tng_control rfm_action_server config/configs/gr00t_so101.yaml
```

## Configuration File Structure

### Basic Structure

```yaml
model:
  type: gr00t  # or octo
  mapper_type: default  # or rtc
  client_type: real  # or mock
  port: 8043

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

