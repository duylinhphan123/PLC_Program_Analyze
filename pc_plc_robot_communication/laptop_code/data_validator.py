#!/usr/bin/env python3
"""
Data Validator
==============

Description: Comprehensive data validation for coordinate exchange system
Purpose: Validates coordinate data, ranges, and system constraints
Version: 1.0
Date: 17/07/2025

Features:
- Coordinate validation
- Range checking
- System constraint validation
- Error reporting
- Configuration-based validation
"""

import json
import logging
import math
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass
class ValidationError:
    """Validation error data structure"""
    field: str
    value: Any
    error_type: str
    message: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO

@dataclass
class ValidationResult:
    """Validation result data structure"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    
    def add_error(self, field: str, value: Any, error_type: str, message: str):
        """Add error to validation result"""
        self.errors.append(ValidationError(field, value, error_type, message, "ERROR"))
        self.is_valid = False
    
    def add_warning(self, field: str, value: Any, error_type: str, message: str):
        """Add warning to validation result"""
        self.warnings.append(ValidationError(field, value, error_type, message, "WARNING"))
    
    def get_error_summary(self) -> str:
        """Get error summary string"""
        if not self.errors and not self.warnings:
            return "Validation passed"
        
        summary = []
        if self.errors:
            summary.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            summary.append(f"{len(self.warnings)} warning(s)")
        
        return ", ".join(summary)

class DataValidator:
    """
    Data Validator Class
    
    Provides comprehensive validation for coordinate exchange system
    """
    
    def __init__(self, config_file: str = "validation_config.json"):
        """
        Initialize data validator
        
        Args:
            config_file: Path to validation configuration file
        """
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load validation configuration
        
        Returns:
            dict: Validation configuration
        """
        default_config = {
            "coordinate_limits": {
                "x_min": -2000, "x_max": 2000,
                "y_min": -2000, "y_max": 2000,
                "z_min": 0, "z_max": 1000
            },
            "rotation_limits": {
                "rx_min": -18000, "rx_max": 18000,  # -180° to 180° * 100
                "ry_min": -18000, "ry_max": 18000,
                "rz_min": -18000, "rz_max": 18000
            },
            "speed_limits": {
                "min": 1, "max": 100,
                "recommended_min": 10,
                "recommended_max": 80
            },
            "area_limits": {
                "1": {
                    "name": "Palletizing Area 1",
                    "x_min": -1500, "x_max": 1500,
                    "y_min": -1500, "y_max": 1500,
                    "z_min": 100, "z_max": 800,
                    "safe_zones": [
                        {"x": [0, 1000], "y": [0, 1000], "z": [200, 600]},
                        {"x": [-1000, 0], "y": [0, 1000], "z": [200, 600]}
                    ]
                },
                "2": {
                    "name": "Palletizing Area 2",
                    "x_min": -1500, "x_max": 1500,
                    "y_min": -1500, "y_max": 1500,
                    "z_min": 100, "z_max": 800,
                    "safe_zones": [
                        {"x": [0, 1000], "y": [-1000, 0], "z": [200, 600]},
                        {"x": [-1000, 0], "y": [-1000, 0], "z": [200, 600]}
                    ]
                }
            },
            "gripper_commands": [0, 1],  # 0=open, 1=close
            "set_limits": {
                "min": 1, "max": 10,
                "max_coordinates_per_set": 20
            },
            "safety_limits": {
                "min_z_clearance": 50,  # Minimum Z height for safety
                "max_velocity": 2000,   # mm/s
                "collision_zones": [
                    {"x": [0, 100], "y": [0, 100], "z": [0, 200], "description": "Fixture"}
                ]
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                self.logger.error(f"Error loading validation config: {e}")
                return default_config
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def validate_coordinate(self, x: int, y: int, z: int, rx: int = 0, ry: int = 0, rz: int = 0,
                          area: Optional[int] = None) -> ValidationResult:
        """
        Validate coordinate values
        
        Args:
            x, y, z: Coordinates in mm
            rx, ry, rz: Rotations in degrees*100
            area: Optional area number for area-specific validation
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Validate coordinate ranges
        coord_limits = self.config["coordinate_limits"]
        
        if not (coord_limits["x_min"] <= x <= coord_limits["x_max"]):
            result.add_error("x", x, "RANGE_ERROR", 
                           f"X coordinate {x} out of range ({coord_limits['x_min']} to {coord_limits['x_max']})")
        
        if not (coord_limits["y_min"] <= y <= coord_limits["y_max"]):
            result.add_error("y", y, "RANGE_ERROR",
                           f"Y coordinate {y} out of range ({coord_limits['y_min']} to {coord_limits['y_max']})")
        
        if not (coord_limits["z_min"] <= z <= coord_limits["z_max"]):
            result.add_error("z", z, "RANGE_ERROR",
                           f"Z coordinate {z} out of range ({coord_limits['z_min']} to {coord_limits['z_max']})")
        
        # Validate rotations
        rot_limits = self.config["rotation_limits"]
        
        if not (rot_limits["rx_min"] <= rx <= rot_limits["rx_max"]):
            result.add_error("rx", rx, "RANGE_ERROR",
                           f"RX rotation {rx} out of range ({rot_limits['rx_min']} to {rot_limits['rx_max']})")
        
        if not (rot_limits["ry_min"] <= ry <= rot_limits["ry_max"]):
            result.add_error("ry", ry, "RANGE_ERROR",
                           f"RY rotation {ry} out of range ({rot_limits['ry_min']} to {rot_limits['ry_max']})")
        
        if not (rot_limits["rz_min"] <= rz <= rot_limits["rz_max"]):
            result.add_error("rz", rz, "RANGE_ERROR",
                           f"RZ rotation {rz} out of range ({rot_limits['rz_min']} to {rot_limits['rz_max']})")
        
        # Area-specific validation
        if area is not None:
            area_result = self.validate_area_coordinate(x, y, z, area)
            result.errors.extend(area_result.errors)
            result.warnings.extend(area_result.warnings)
            if not area_result.is_valid:
                result.is_valid = False
        
        # Safety validation
        safety_result = self.validate_safety_constraints(x, y, z)
        result.errors.extend(safety_result.errors)
        result.warnings.extend(safety_result.warnings)
        if not safety_result.is_valid:
            result.is_valid = False
        
        return result
    
    def validate_area_coordinate(self, x: int, y: int, z: int, area: int) -> ValidationResult:
        """
        Validate coordinate for specific area
        
        Args:
            x, y, z: Coordinates in mm
            area: Area number
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        if str(area) not in self.config["area_limits"]:
            result.add_error("area", area, "INVALID_AREA", f"Area {area} not configured")
            return result
        
        area_config = self.config["area_limits"][str(area)]
        
        # Check area limits
        if not (area_config["x_min"] <= x <= area_config["x_max"]):
            result.add_error("x", x, "AREA_RANGE_ERROR",
                           f"X coordinate {x} out of area {area} range ({area_config['x_min']} to {area_config['x_max']})")
        
        if not (area_config["y_min"] <= y <= area_config["y_max"]):
            result.add_error("y", y, "AREA_RANGE_ERROR",
                           f"Y coordinate {y} out of area {area} range ({area_config['y_min']} to {area_config['y_max']})")
        
        if not (area_config["z_min"] <= z <= area_config["z_max"]):
            result.add_error("z", z, "AREA_RANGE_ERROR",
                           f"Z coordinate {z} out of area {area} range ({area_config['z_min']} to {area_config['z_max']})")
        
        # Check safe zones (warning if outside)
        if "safe_zones" in area_config:
            in_safe_zone = False
            for safe_zone in area_config["safe_zones"]:
                if (safe_zone["x"][0] <= x <= safe_zone["x"][1] and
                    safe_zone["y"][0] <= y <= safe_zone["y"][1] and
                    safe_zone["z"][0] <= z <= safe_zone["z"][1]):
                    in_safe_zone = True
                    break
            
            if not in_safe_zone:
                result.add_warning("position", [x, y, z], "OUTSIDE_SAFE_ZONE",
                                 f"Position [{x}, {y}, {z}] is outside safe zones for area {area}")
        
        return result
    
    def validate_safety_constraints(self, x: int, y: int, z: int) -> ValidationResult:
        """
        Validate safety constraints
        
        Args:
            x, y, z: Coordinates in mm
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        safety_config = self.config["safety_limits"]
        
        # Check minimum Z clearance
        if z < safety_config["min_z_clearance"]:
            result.add_error("z", z, "SAFETY_VIOLATION",
                           f"Z coordinate {z} below minimum clearance {safety_config['min_z_clearance']}")
        
        # Check collision zones
        for collision_zone in safety_config["collision_zones"]:
            if (collision_zone["x"][0] <= x <= collision_zone["x"][1] and
                collision_zone["y"][0] <= y <= collision_zone["y"][1] and
                collision_zone["z"][0] <= z <= collision_zone["z"][1]):
                result.add_error("position", [x, y, z], "COLLISION_ZONE",
                               f"Position [{x}, {y}, {z}] in collision zone: {collision_zone['description']}")
        
        return result
    
    def validate_speed(self, speed: int) -> ValidationResult:
        """
        Validate speed value
        
        Args:
            speed: Speed override (1-100%)
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        speed_limits = self.config["speed_limits"]
        
        if not (speed_limits["min"] <= speed <= speed_limits["max"]):
            result.add_error("speed", speed, "RANGE_ERROR",
                           f"Speed {speed} out of range ({speed_limits['min']} to {speed_limits['max']})")
        
        # Warnings for non-recommended speeds
        if speed < speed_limits["recommended_min"]:
            result.add_warning("speed", speed, "LOW_SPEED",
                             f"Speed {speed} below recommended minimum {speed_limits['recommended_min']}")
        
        if speed > speed_limits["recommended_max"]:
            result.add_warning("speed", speed, "HIGH_SPEED",
                             f"Speed {speed} above recommended maximum {speed_limits['recommended_max']}")
        
        return result
    
    def validate_gripper(self, gripper: int) -> ValidationResult:
        """
        Validate gripper command
        
        Args:
            gripper: Gripper command
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        if gripper not in self.config["gripper_commands"]:
            result.add_error("gripper", gripper, "INVALID_COMMAND",
                           f"Gripper command {gripper} not in valid commands {self.config['gripper_commands']}")
        
        return result
    
    def validate_area_and_set(self, area: int, set_number: int) -> ValidationResult:
        """
        Validate area and set number
        
        Args:
            area: Area number
            set_number: Set number
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Validate area
        if str(area) not in self.config["area_limits"]:
            result.add_error("area", area, "INVALID_AREA", f"Area {area} not configured")
        
        # Validate set number
        set_limits = self.config["set_limits"]
        if not (set_limits["min"] <= set_number <= set_limits["max"]):
            result.add_error("set_number", set_number, "RANGE_ERROR",
                           f"Set number {set_number} out of range ({set_limits['min']} to {set_limits['max']})")
        
        return result
    
    def validate_coordinate_set(self, coordinates: List[Dict[str, Any]], area: int, set_number: int) -> ValidationResult:
        """
        Validate complete coordinate set
        
        Args:
            coordinates: List of coordinate dictionaries
            area: Area number
            set_number: Set number
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Validate area and set
        area_set_result = self.validate_area_and_set(area, set_number)
        result.errors.extend(area_set_result.errors)
        result.warnings.extend(area_set_result.warnings)
        if not area_set_result.is_valid:
            result.is_valid = False
        
        # Validate coordinate count
        set_limits = self.config["set_limits"]
        if len(coordinates) > set_limits["max_coordinates_per_set"]:
            result.add_error("coordinates", len(coordinates), "TOO_MANY_COORDINATES",
                           f"Too many coordinates {len(coordinates)}, maximum {set_limits['max_coordinates_per_set']}")
        
        if len(coordinates) == 0:
            result.add_error("coordinates", 0, "EMPTY_SET", "Coordinate set cannot be empty")
        
        # Validate each coordinate
        for i, coord in enumerate(coordinates):
            coord_result = self.validate_coordinate(
                coord.get('x', 0), coord.get('y', 0), coord.get('z', 0),
                coord.get('rx', 0), coord.get('ry', 0), coord.get('rz', 0),
                area
            )
            
            # Add coordinate index to error messages
            for error in coord_result.errors:
                error.field = f"coordinate[{i}].{error.field}"
                result.errors.append(error)
            
            for warning in coord_result.warnings:
                warning.field = f"coordinate[{i}].{warning.field}"
                result.warnings.append(warning)
            
            if not coord_result.is_valid:
                result.is_valid = False
            
            # Validate speed and gripper for each coordinate
            speed_result = self.validate_speed(coord.get('speed', 50))
            gripper_result = self.validate_gripper(coord.get('gripper', 0))
            
            for error in speed_result.errors:
                error.field = f"coordinate[{i}].{error.field}"
                result.errors.append(error)
            
            for error in gripper_result.errors:
                error.field = f"coordinate[{i}].{error.field}"
                result.errors.append(error)
            
            if not speed_result.is_valid or not gripper_result.is_valid:
                result.is_valid = False
        
        return result
    
    def validate_motion_path(self, start_coord: Dict[str, Any], end_coord: Dict[str, Any]) -> ValidationResult:
        """
        Validate motion path between two coordinates
        
        Args:
            start_coord: Starting coordinate
            end_coord: Ending coordinate
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Calculate distance
        dx = end_coord['x'] - start_coord['x']
        dy = end_coord['y'] - start_coord['y']
        dz = end_coord['z'] - start_coord['z']
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Check maximum distance
        max_distance = 3000  # mm
        if distance > max_distance:
            result.add_warning("distance", distance, "LONG_DISTANCE",
                             f"Motion distance {distance:.1f}mm exceeds recommended maximum {max_distance}mm")
        
        # Check Z motion direction
        if dz < -500:  # Large downward motion
            result.add_warning("z_motion", dz, "RAPID_DESCENT",
                             f"Rapid Z descent {dz}mm, verify safety")
        
        # Check for potential collisions along path
        # Simple linear interpolation check
        steps = max(1, int(distance / 100))  # Check every 100mm
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            check_x = int(start_coord['x'] + t * dx)
            check_y = int(start_coord['y'] + t * dy)
            check_z = int(start_coord['z'] + t * dz)
            
            safety_result = self.validate_safety_constraints(check_x, check_y, check_z)
            if not safety_result.is_valid:
                result.add_error("path", [check_x, check_y, check_z], "PATH_COLLISION",
                               f"Path collision at [{check_x}, {check_y}, {check_z}]")
                result.is_valid = False
                break
        
        return result
    
    def validate_command_data(self, command_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate command data structure
        
        Args:
            command_data: Command data dictionary
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        required_fields = ['command_word', 'area_selection', 'coordinate_set']
        
        # Check required fields
        for field in required_fields:
            if field not in command_data:
                result.add_error(field, None, "MISSING_FIELD", f"Required field {field} missing")
        
        # Validate command word
        valid_commands = list(range(11))  # 0-10
        if 'command_word' in command_data:
            if command_data['command_word'] not in valid_commands:
                result.add_error("command_word", command_data['command_word'], "INVALID_COMMAND",
                               f"Invalid command {command_data['command_word']}")
        
        # Validate area and set if present
        if 'area_selection' in command_data and 'coordinate_set' in command_data:
            area_result = self.validate_area_and_set(
                command_data['area_selection'],
                command_data['coordinate_set']
            )
            result.errors.extend(area_result.errors)
            result.warnings.extend(area_result.warnings)
            if not area_result.is_valid:
                result.is_valid = False
        
        return result
    
    def get_validation_report(self, result: ValidationResult) -> str:
        """
        Generate validation report
        
        Args:
            result: Validation result
            
        Returns:
            str: Formatted validation report
        """
        report = []
        report.append(f"Validation Result: {'PASSED' if result.is_valid else 'FAILED'}")
        report.append(f"Summary: {result.get_error_summary()}")
        
        if result.errors:
            report.append("\nERRORS:")
            for error in result.errors:
                report.append(f"  - {error.field}: {error.message} (value: {error.value})")
        
        if result.warnings:
            report.append("\nWARNINGS:")
            for warning in result.warnings:
                report.append(f"  - {warning.field}: {warning.message} (value: {warning.value})")
        
        return "\n".join(report)

# Example usage
if __name__ == "__main__":
    validator = DataValidator()
    
    # Test coordinate validation
    result = validator.validate_coordinate(1000, 500, 300, area=1)
    print(validator.get_validation_report(result))
    
    # Test coordinate set validation
    coordinates = [
        {'x': 1000, 'y': 500, 'z': 300, 'rx': 0, 'ry': 0, 'rz': 0, 'gripper': 1, 'speed': 50},
        {'x': 1200, 'y': 600, 'z': 400, 'rx': 0, 'ry': 0, 'rz': 0, 'gripper': 0, 'speed': 75}
    ]
    result = validator.validate_coordinate_set(coordinates, area=1, set_number=1)
    print(validator.get_validation_report(result))
