# YAML Configuration Schema & Validation

This directory contains Pydantic-based schema validation for RFM (Robot Foundation Model) configurations.

## ✨ Features

### 1. **Automatic Validation**
All YAML configurations are automatically validated when loaded:

```python
from rfm_control.config.config_loader import ConfigLoader

# Validation happens automatically!
config = ConfigLoader.load_yaml("config/configs/gr00t_so101.yaml")
# ✅ Returns validated config or raises ValidationError
```

### 2. **Type Safety**
Pydantic ensures type correctness:

```yaml
# ❌ This will fail validation:
model:
  port: "not_a_number"  # Must be int!
  type: "invalid_type"  # Must be "gr00t" or "octo"!

# ✅ This will pass:
model:
  port: 8043
  type: "gr00t"
```

### 3. **Field Validation**
Built-in validators check constraints:

- `port`: Must be between 1-65535
- `time_between_goals`: Must be >= 0.0
- `resolution`: Must be exactly 2 values [width, height]
- `robots`: At least one robot required
- Robot prefixes must be unique

### 4. **Helpful Error Messages**

```
Configuration validation failed for gr00t_so101.yaml:
2 validation errors for RfmConfigYaml
model.port
  Input should be greater than or equal to 1 [type=greater_than_equal, ...]
robots.0.arm.model_input_position_key
  Field required [type=missing, ...]
```

## 🔧 Tools

### Generate JSON Schema

Generate a JSON Schema for IDE autocomplete and validation:

```bash
python -m rfm_control.config.generate_schema
# Creates: rfm_config_schema.json
```

Use this schema in your IDE (VS Code, PyCharm) for:
- Autocomplete in YAML files
- Real-time validation
- Documentation tooltips

### Validate YAML Files

Validate a single file:

```bash
python -m rfm_control.config.validate_yaml config/configs/gr00t_so101.yaml
```

Validate all configs in a directory:

```bash
python -m rfm_control.config.validate_yaml -d config/configs/
```

## 📝 Schema Documentation

### Complete Configuration Structure

```yaml
model:
  type: "gr00t" | "octo"           # Required
  mapper_type: "default" | "rtc"   # Default: "default"
  client_type: "real" | "mock" # Default: "real"
  port: 1-65535                    # Default: 8043

robots:  # At least one required, prefixes must be unique
  - prefix: ""                     # Robot ID (empty for single robot)
    group_name: "arm"              # MoveIt group
    frame_id: "world"              # Reference frame
    joint_state_topic: "/joint_states"
    time_between_goals: 0.5        # >= 0.0
    
    arm:
      topic_name: "/arm_controller/follow_joint_trajectory"
      model_input_position_key: "state.single_arm"     # Required
      model_input_velocity_key: ""                     # Optional
      model_input_load_key: ""                         # Optional
      model_output_position_key: "action.single_arm"   # Required
      model_output_velocity_key: ""                    # Optional
    
    gripper:
      # Same structure as arm
      ...

images:  # Optional, can be empty list
  - model_input_key: "video.wrist"                    # Required
    topic_name: "/wrist/image_raw/compressed"         # Required
    resolution: [640, 480]                            # Exactly 2 values
    image_type: "compressed" | "raw"                  # Default: "compressed"
    transformation: "identity" | "gr00t" | "octo"     # Default: "identity"
```

## 🔄 Adding New Fields

### Step 1: Update Pydantic Schema

Edit `config_schema.py`:

```python
class ArmConfig(BaseModel):
    # Add new field with validation
    new_field: str = Field(
        default="default_value",
        description="What this field does",
        examples=["example1", "example2"]
    )
```

### Step 2: Update YAML Files

Add the new field to your YAML configs:

```yaml
arm:
  topic_name: "/arm_controller/follow_joint_trajectory"
  new_field: "my_value"  # ← New field
  # ... rest of fields
```

### Step 3: Validate

```bash
# Check all configs still validate
python -m rfm_control.config.validate_yaml -d config/configs/
```

**That's it!** No manual mapping code needed in `config_loader.py` anymore! 🎉

## 📚 Pydantic Benefits

1. **Automatic Parsing**: YAML → Python objects automatically
2. **Type Coercion**: `"8043"` → `8043` (string to int)
3. **Default Values**: Missing optional fields get defaults
4. **Validation**: Built-in validators (ranges, types, patterns)
5. **Documentation**: Schema can generate docs automatically
6. **IDE Support**: JSON Schema enables autocomplete

## 🔍 VS Code Integration

Add to your `settings.json`:

```json
{
  "yaml.schemas": {
    "rfm_control/config/rfm_config_schema.json": "config/configs/*.yaml"
  }
}
```

Now you get:
- ✅ Autocomplete
- ✅ Inline validation
- ✅ Documentation on hover

## 🧪 Testing

### Automated Tests

The configuration validation is covered by comprehensive automated tests:

```bash
# Run all config validation tests
cd /path/to/rfm_control
python3 -m pytest test/test_config_validation.py -v

# Quick summary
python3 -m pytest test/test_config_validation.py -q
```

**Test Coverage**: 20 tests covering:
- Invalid configurations (port ranges, missing fields, invalid types)
- Valid configurations (minimal, with images, dual robots)
- Edge cases (boundary values, empty strings, type coercion)
- Default value handling

See [`test/README.md`](../../../test/README.md) for detailed test documentation.

### Manual Testing

Test validation in your code:

```python
from pydantic import ValidationError
from rfm_control.config.config_loader import ConfigLoader

try:
    config = ConfigLoader.load_yaml("my_config.yaml")
    print("✅ Valid!")
except ValidationError as e:
    print(f"❌ Invalid: {e}")
```

## 📖 More Info

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JSON Schema Specification](https://json-schema.org/)
- [YAML Specification](https://yaml.org/)

