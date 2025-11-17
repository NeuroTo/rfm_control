#!/usr/bin/env python3
"""Validate YAML configuration files against Pydantic schema."""
import sys
from pathlib import Path
from pydantic import ValidationError

from tng_control.rfm_control.config.config_loader import ConfigLoader


def validate_yaml_file(yaml_path: str | Path) -> bool:
    """
    Validate a YAML configuration file.
    
    Args:
        yaml_path: Path to YAML file to validate
        
    Returns:
        True if valid, False otherwise
    """
    yaml_path = Path(yaml_path)
    
    print(f"🔍 Validating: {yaml_path}")
    
    try:
        config = ConfigLoader.load_yaml(yaml_path)
        print(f"✅ Valid configuration!")
        print(f"   Model type: {config.model.type}")
        print(f"   Robots: {len(config.robots)}")
        print(f"   Images: {len(config.images)}")
        return True
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return False
        
    except ValueError as e:
        print(f"❌ Validation failed:")
        print(f"   {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def validate_directory(directory: str | Path) -> dict[str, bool]:
    """
    Validate all YAML files in a directory.
    
    Args:
        directory: Path to directory containing YAML files
        
    Returns:
        Dictionary mapping file paths to validation results
    """
    directory = Path(directory)
    yaml_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
    
    if not yaml_files:
        print(f"⚠️  No YAML files found in {directory}")
        return {}
    
    results = {}
    for yaml_file in yaml_files:
        results[str(yaml_file)] = validate_yaml_file(yaml_file)
        print()
    
    # Summary
    valid_count = sum(results.values())
    total_count = len(results)
    
    print("=" * 60)
    print(f"Summary: {valid_count}/{total_count} files valid")
    
    if valid_count == total_count:
        print("✅ All configurations are valid!")
    else:
        print("❌ Some configurations have errors")
        for path, is_valid in results.items():
            if not is_valid:
                print(f"   - {path}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate YAML configuration files")
    parser.add_argument(
        "path",
        help="Path to YAML file or directory to validate"
    )
    parser.add_argument(
        "-d", "--directory",
        action="store_true",
        help="Validate all YAML files in directory"
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if args.directory or path.is_dir():
        results = validate_directory(path)
        sys.exit(0 if all(results.values()) else 1)
    else:
        is_valid = validate_yaml_file(path)
        sys.exit(0 if is_valid else 1)



