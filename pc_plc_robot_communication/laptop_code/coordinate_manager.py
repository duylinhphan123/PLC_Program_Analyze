#!/usr/bin/env python3
"""
Coordinate Manager
==================

Description: High-level coordinate management for PC-PLC-Robot communication
Purpose: Manages coordinate sets, validates data, and provides abstraction layer
Version: 1.0
Date: 17/07/2025

Features:
- Coordinate set management
- Data validation
- Area management
- Batch operations
- Error handling
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from plc_client import PLCClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass
class Coordinate:
    """
    Coordinate data structure
    """
    x: int  # X coordinate in mm
    y: int  # Y coordinate in mm
    z: int  # Z coordinate in mm
    rx: int = 0  # X rotation in degrees*100
    ry: int = 0  # Y rotation in degrees*100
    rz: int = 0  # Z rotation in degrees*100
    gripper: int = 0  # Gripper command (0=open, 1=close)
    speed: int = 50  # Speed override (10-100%)
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate coordinate data
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check coordinate ranges (example limits)
        if not (-2000 <= self.x <= 2000):
            return False, f"X coordinate {self.x} out of range (-2000 to 2000)"
        if not (-2000 <= self.y <= 2000):
            return False, f"Y coordinate {self.y} out of range (-2000 to 2000)"
        if not (0 <= self.z <= 1000):
            return False, f"Z coordinate {self.z} out of range (0 to 1000)"
        
        # Check rotation ranges
        if not (-18000 <= self.rx <= 18000):
            return False, f"RX rotation {self.rx} out of range (-180° to 180°)"
        if not (-18000 <= self.ry <= 18000):
            return False, f"RY rotation {self.ry} out of range (-180° to 180°)"
        if not (-18000 <= self.rz <= 18000):
            return False, f"RZ rotation {self.rz} out of range (-180° to 180°)"
        
        # Check gripper command
        if self.gripper not in [0, 1]:
            return False, f"Gripper command {self.gripper} must be 0 or 1"
        
        # Check speed
        if not (10 <= self.speed <= 100):
            return False, f"Speed {self.speed} out of range (10 to 100)"
        
        return True, "Valid"

@dataclass
class CoordinateSet:
    """
    Coordinate set data structure
    """
    area: int  # Area number (1 or 2)
    set_number: int  # Set number (1-10)
    coordinates: List[Coordinate]  # List of coordinates
    description: str = ""  # Optional description
    created_at: str = ""  # Creation timestamp
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate coordinate set
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check area
        if self.area not in [1, 2]:
            return False, f"Area {self.area} must be 1 or 2"
        
        # Check set number
        if not (1 <= self.set_number <= 10):
            return False, f"Set number {self.set_number} must be 1-10"
        
        # Check coordinates
        if not self.coordinates:
            return False, "Coordinate set cannot be empty"
        
        if len(self.coordinates) > 20:
            return False, "Maximum 20 coordinates per set"
        
        # Validate each coordinate
        for i, coord in enumerate(self.coordinates):
            is_valid, error = coord.validate()
            if not is_valid:
                return False, f"Coordinate {i+1}: {error}"
        
        return True, "Valid"

class CoordinateManager:
    """
    Coordinate Manager Class
    
    Manages coordinate sets and provides high-level interface
    """
    
    def __init__(self, plc_client: PLCClient, config_file: str = "coordinate_config.json"):
        """
        Initialize coordinate manager
        
        Args:
            plc_client: PLC client instance
            config_file: Configuration file path
        """
        self.plc_client = plc_client
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        self.coordinate_sets: Dict[Tuple[int, int], CoordinateSet] = {}
        self.lock = threading.Lock()
        
        # Load configuration
        self.config = self.load_config()
        
        # Load saved coordinate sets
        self.load_coordinate_sets()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            dict: Configuration data
        """
        default_config = {
            "areas": {
                "1": {
                    "name": "Palletizing Area 1",
                    "limits": {
                        "x_min": -1500, "x_max": 1500,
                        "y_min": -1500, "y_max": 1500,
                        "z_min": 0, "z_max": 800
                    }
                },
                "2": {
                    "name": "Palletizing Area 2", 
                    "limits": {
                        "x_min": -1500, "x_max": 1500,
                        "y_min": -1500, "y_max": 1500,
                        "z_min": 0, "z_max": 800
                    }
                }
            },
            "defaults": {
                "speed": 50,
                "gripper": 0,
                "timeout": 30
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
                self.logger.error(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def load_coordinate_sets(self):
        """Load coordinate sets from file"""
        sets_file = Path("coordinate_sets.json")
        if sets_file.exists():
            try:
                with open(sets_file, 'r') as f:
                    data = json.load(f)
                    for key, set_data in data.items():
                        area, set_number = eval(key)  # Convert string key back to tuple
                        coordinates = [Coordinate(**coord) for coord in set_data['coordinates']]
                        coord_set = CoordinateSet(
                            area=area,
                            set_number=set_number,
                            coordinates=coordinates,
                            description=set_data.get('description', ''),
                            created_at=set_data.get('created_at', '')
                        )
                        self.coordinate_sets[(area, set_number)] = coord_set
                        
            except Exception as e:
                self.logger.error(f"Error loading coordinate sets: {e}")
    
    def save_coordinate_sets(self):
        """Save coordinate sets to file"""
        try:
            data = {}
            for key, coord_set in self.coordinate_sets.items():
                data[str(key)] = {
                    'area': coord_set.area,
                    'set_number': coord_set.set_number,
                    'coordinates': [asdict(coord) for coord in coord_set.coordinates],
                    'description': coord_set.description,
                    'created_at': coord_set.created_at
                }
            
            with open("coordinate_sets.json", 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving coordinate sets: {e}")
    
    def add_coordinate_set(self, coord_set: CoordinateSet) -> bool:
        """
        Add coordinate set
        
        Args:
            coord_set: Coordinate set to add
            
        Returns:
            bool: True if successful
        """
        # Validate coordinate set
        is_valid, error = coord_set.validate()
        if not is_valid:
            self.logger.error(f"Invalid coordinate set: {error}")
            return False
        
        with self.lock:
            key = (coord_set.area, coord_set.set_number)
            self.coordinate_sets[key] = coord_set
            self.save_coordinate_sets()
            
        self.logger.info(f"Added coordinate set {coord_set.set_number} to area {coord_set.area}")
        return True
    
    def get_coordinate_set(self, area: int, set_number: int) -> Optional[CoordinateSet]:
        """
        Get coordinate set
        
        Args:
            area: Area number
            set_number: Set number
            
        Returns:
            CoordinateSet or None
        """
        with self.lock:
            return self.coordinate_sets.get((area, set_number))
    
    def delete_coordinate_set(self, area: int, set_number: int) -> bool:
        """
        Delete coordinate set
        
        Args:
            area: Area number
            set_number: Set number
            
        Returns:
            bool: True if successful
        """
        with self.lock:
            key = (area, set_number)
            if key in self.coordinate_sets:
                del self.coordinate_sets[key]
                self.save_coordinate_sets()
                self.logger.info(f"Deleted coordinate set {set_number} from area {area}")
                return True
            else:
                self.logger.error(f"Coordinate set {set_number} not found in area {area}")
                return False
    
    def list_coordinate_sets(self, area: Optional[int] = None) -> List[CoordinateSet]:
        """
        List coordinate sets
        
        Args:
            area: Optional area filter
            
        Returns:
            List of coordinate sets
        """
        with self.lock:
            if area is None:
                return list(self.coordinate_sets.values())
            else:
                return [coord_set for (a, _), coord_set in self.coordinate_sets.items() if a == area]
    
    def write_coordinate_set_to_plc(self, area: int, set_number: int) -> bool:
        """
        Write coordinate set to PLC
        
        Args:
            area: Area number
            set_number: Set number
            
        Returns:
            bool: True if successful
        """
        coord_set = self.get_coordinate_set(area, set_number)
        if not coord_set:
            self.logger.error(f"Coordinate set {set_number} not found in area {area}")
            return False
        
        # Write first coordinate to PLC (for simplicity, could be extended for multiple coordinates)
        if coord_set.coordinates:
            coord = coord_set.coordinates[0]
            success = self.plc_client.write_coordinate_set(
                area=area,
                set_number=set_number,
                x=coord.x,
                y=coord.y,
                z=coord.z,
                rx=coord.rx,
                ry=coord.ry,
                rz=coord.rz,
                gripper=coord.gripper,
                speed=coord.speed
            )
            
            if success:
                self.logger.info(f"Coordinate set {set_number} written to PLC for area {area}")
            else:
                self.logger.error(f"Failed to write coordinate set {set_number} to PLC")
                
            return success
        
        return False
    
    def execute_coordinate_set(self, area: int, set_number: int) -> bool:
        """
        Execute coordinate set
        
        Args:
            area: Area number
            set_number: Set number
            
        Returns:
            bool: True if successful
        """
        # First write to PLC, then execute
        if self.write_coordinate_set_to_plc(area, set_number):
            return self.plc_client.execute_coordinate_set(area, set_number)
        return False
    
    def execute_sequence(self, sequences: List[Tuple[int, int]]) -> bool:
        """
        Execute sequence of coordinate sets
        
        Args:
            sequences: List of (area, set_number) tuples
            
        Returns:
            bool: True if all successful
        """
        for area, set_number in sequences:
            success = self.execute_coordinate_set(area, set_number)
            if not success:
                self.logger.error(f"Failed to execute coordinate set {set_number} in area {area}")
                return False
            
            # Wait for completion before next set
            time.sleep(0.5)
        
        return True
    
    def create_coordinate_from_current_position(self, area: int, set_number: int, 
                                              description: str = "") -> bool:
        """
        Create coordinate set from current robot position
        
        Args:
            area: Area number
            set_number: Set number
            description: Optional description
            
        Returns:
            bool: True if successful
        """
        current_pos = self.plc_client.get_current_position()
        if not current_pos:
            self.logger.error("Failed to get current position")
            return False
        
        coord = Coordinate(
            x=current_pos['x'],
            y=current_pos['y'],
            z=current_pos['z'],
            rx=current_pos['rx'],
            ry=current_pos['ry'],
            rz=current_pos['rz'],
            gripper=current_pos['gripper'],
            speed=self.config['defaults']['speed']
        )
        
        coord_set = CoordinateSet(
            area=area,
            set_number=set_number,
            coordinates=[coord],
            description=description or f"Captured position at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return self.add_coordinate_set(coord_set)
    
    def import_coordinates_from_file(self, file_path: str) -> bool:
        """
        Import coordinates from CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            bool: True if successful
        """
        try:
            import csv
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    coord = Coordinate(
                        x=int(row['x']),
                        y=int(row['y']),
                        z=int(row['z']),
                        rx=int(row.get('rx', 0)),
                        ry=int(row.get('ry', 0)),
                        rz=int(row.get('rz', 0)),
                        gripper=int(row.get('gripper', 0)),
                        speed=int(row.get('speed', 50))
                    )
                    
                    coord_set = CoordinateSet(
                        area=int(row['area']),
                        set_number=int(row['set_number']),
                        coordinates=[coord],
                        description=row.get('description', '')
                    )
                    
                    self.add_coordinate_set(coord_set)
            
            self.logger.info(f"Imported coordinates from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing coordinates: {e}")
            return False
    
    def export_coordinates_to_file(self, file_path: str, area: Optional[int] = None) -> bool:
        """
        Export coordinates to CSV file
        
        Args:
            file_path: Path to output CSV file
            area: Optional area filter
            
        Returns:
            bool: True if successful
        """
        try:
            import csv
            with open(file_path, 'w', newline='') as f:
                fieldnames = ['area', 'set_number', 'x', 'y', 'z', 'rx', 'ry', 'rz', 
                             'gripper', 'speed', 'description', 'created_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                coord_sets = self.list_coordinate_sets(area)
                for coord_set in coord_sets:
                    for coord in coord_set.coordinates:
                        writer.writerow({
                            'area': coord_set.area,
                            'set_number': coord_set.set_number,
                            'x': coord.x,
                            'y': coord.y,
                            'z': coord.z,
                            'rx': coord.rx,
                            'ry': coord.ry,
                            'rz': coord.rz,
                            'gripper': coord.gripper,
                            'speed': coord.speed,
                            'description': coord_set.description,
                            'created_at': coord_set.created_at
                        })
            
            self.logger.info(f"Exported coordinates to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting coordinates: {e}")
            return False
    
    def get_area_statistics(self, area: int) -> Dict[str, Any]:
        """
        Get area statistics
        
        Args:
            area: Area number
            
        Returns:
            dict: Statistics
        """
        coord_sets = self.list_coordinate_sets(area)
        total_coordinates = sum(len(cs.coordinates) for cs in coord_sets)
        
        return {
            'area': area,
            'total_sets': len(coord_sets),
            'total_coordinates': total_coordinates,
            'sets': [cs.set_number for cs in coord_sets],
            'area_name': self.config['areas'][str(area)]['name']
        }

# Example usage
if __name__ == "__main__":
    # Create PLC client and coordinate manager
    plc_client = PLCClient("192.168.1.100")
    coord_manager = CoordinateManager(plc_client)
    
    if plc_client.connect():
        # Example: Create and add a coordinate set
        coord = Coordinate(x=1000, y=500, z=300, gripper=1, speed=75)
        coord_set = CoordinateSet(
            area=1,
            set_number=1,
            coordinates=[coord],
            description="Test coordinate set"
        )
        
        if coord_manager.add_coordinate_set(coord_set):
            print("Coordinate set added successfully")
            
            # Execute the coordinate set
            if coord_manager.execute_coordinate_set(1, 1):
                print("Coordinate set executed successfully")
            else:
                print("Failed to execute coordinate set")
        else:
            print("Failed to add coordinate set")
    else:
        print("Failed to connect to PLC")
    
    plc_client.disconnect()
