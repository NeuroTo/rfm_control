#!/usr/bin/env python3
"""Generate JSON Schema from Pydantic models for YAML validation."""
import json
import sys
from pathlib import Path

# Add package to Python path for direct execution without installation
_script_dir = Path(__file__).resolve().parent
_package_root = _script_dir.parent.parent.parent
if str(_package_root) not in sys.path:
    sys.path.insert(0, str(_package_root))

from tng_control.config.config_schema import RfmConfigYaml


def generate_json_schema(output_path: str | Path = "rfm_config_schema.json"):
    """
    Generate JSON Schema from RfmConfigYaml Pydantic model.
    
    This schema can be used for:
    - IDE autocomplete and validation
    - CI/CD validation pipelines
    - Documentation generation
    
    Args:
        output_path: Path where JSON schema will be saved
    """
    schema = RfmConfigYaml.model_json_schema()
    
    output_path = Path(output_path)
    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ JSON Schema generated: {output_path}")
    print(f"   Fields: {len(schema.get('properties', {}))}")
    print(f"   Required: {schema.get('required', [])}")
    
    return schema


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate JSON Schema for RFM config")
    parser.add_argument(
        "-o", "--output",
        default="rfm_config_schema.json",
        help="Output path for JSON schema file"
    )
    
    args = parser.parse_args()
    generate_json_schema(args.output)


