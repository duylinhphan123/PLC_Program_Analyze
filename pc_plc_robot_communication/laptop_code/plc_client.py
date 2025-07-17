#!/usr/bin/env python3
"""
PLC S7 Communication Client
============================

Description: Python client for communicating with Siemens S7 PLC
Purpose: Laptop-side interface for coordinate exchange system
Protocol: S7 protocol over Ethernet TCP/IP
Version: 1.0
Date: 17/07/2025

Requirements:
- python-snap7 library: pip install python-snap7
- Snap7 library installed on system
- Network access to PLC on port 102
"""

import snap7
import struct
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PLCClient:
    """
    PLC S7 Communication Client
    
    Handles communication with Siemens S7-400H PLC for coordinate exchange
    """
    
    def __init__(self, plc_ip: str = "192.168.1.100", rack: int = 0, slot: int = 2):
        """
        Initialize PLC client
        
        Args:
            plc_ip: PLC IP address
            rack: PLC rack number (usually 0)
            slot: PLC slot number (usually 2 for CPU)
        """
        self.plc_ip = plc_ip
        self.rack = rack
        self.slot = slot
        self.client = snap7.client.Client()
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
        # Data block addresses
        self.DB100_NUMBER = 100  # Laptop interface
        self.DB101_NUMBER = 101  # Robot interface
        self.DB102_NUMBER = 102  # Coordinate storage
        
        # Command codes
        self.COMMANDS = {
            'NO_COMMAND': 0,
            'WRITE_COORDINATE': 1,
            'READ_COORDINATE': 2,
            'EXECUTE_COORDINATE': 3,
            'GET_POSITION': 4,
            'STOP_MOTION': 5,
            'RESET_ERROR': 6,
            'GET_STATUS': 7,
            'EMERGENCY_STOP': 8,
            'CLEAR_ALL': 9,
            'VALIDATE_COORDINATE': 10
        }
        
        # Status codes
        self.STATUS = {
            0: 'IDLE',
            1: 'COMMAND_RECEIVED',
            2: 'PROCESSING',
            3: 'COMPLETED',
            4: 'ERROR',
            5: 'WARNING',
            6: 'BUSY',
            7: 'ROBOT_NOT_READY',
            8: 'COMMUNICATION_ERROR',
            9: 'VALIDATION_FAILED',
            10: 'TIMEOUT'
        }
        
    def connect(self) -> bool:
        """
        Connect to PLC
        
        Returns:
            bool: True if connected successfully
        """
        try:
            self.client.connect(self.plc_ip, self.rack, self.slot)
            self.connected = True
            self.logger.info(f"Connected to PLC at {self.plc_ip}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from PLC"""
        if self.connected:
            self.client.disconnect()
            self.connected = False
            self.logger.info("Disconnected from PLC")
    
    def read_db100(self) -> Dict[str, Any]:
        """
        Read DB100 - Laptop Interface
        
        Returns:
            dict: DB100 data structure
        """
        if not self.connected:
            raise Exception("Not connected to PLC")
        
        try:
            # Read 100 bytes from DB100
            data = self.client.db_read(self.DB100_NUMBER, 0, 100)
            
            # Unpack data according to DB100 structure
            result = {
                'command_word': struct.unpack('>H', data[0:2])[0],
                'status_word': struct.unpack('>H', data[2:4])[0],
                'area_selection': struct.unpack('>H', data[4:6])[0],
                'coordinate_set': struct.unpack('>H', data[6:8])[0],
                'x_coordinate': struct.unpack('>l', data[8:12])[0],
                'y_coordinate': struct.unpack('>l', data[12:16])[0],
                'z_coordinate': struct.unpack('>l', data[16:20])[0],
                'rx_rotation': struct.unpack('>h', data[20:22])[0],
                'ry_rotation': struct.unpack('>h', data[22:24])[0],
                'rz_rotation': struct.unpack('>h', data[24:26])[0],
                'gripper_status': struct.unpack('>H', data[26:28])[0],
                'speed_override': struct.unpack('>H', data[28:30])[0],
                'motion_type': struct.unpack('>H', data[30:32])[0],
                'precision': struct.unpack('>H', data[32:34])[0],
                'timestamp_high': struct.unpack('>L', data[34:38])[0],
                'timestamp_low': struct.unpack('>L', data[38:42])[0],
                'error_code': struct.unpack('>H', data[42:44])[0]
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error reading DB100: {e}")
            raise
    
    def write_db100(self, data: Dict[str, Any]) -> bool:
        """
        Write to DB100 - Laptop Interface
        
        Args:
            data: Dictionary with DB100 fields
            
        Returns:
            bool: True if write successful
        """
        if not self.connected:
            raise Exception("Not connected to PLC")
        
        try:
            # Pack data according to DB100 structure
            packed_data = bytearray(100)
            
            # Pack each field
            struct.pack_into('>H', packed_data, 0, data.get('command_word', 0))
            struct.pack_into('>H', packed_data, 2, data.get('status_word', 0))
            struct.pack_into('>H', packed_data, 4, data.get('area_selection', 1))
            struct.pack_into('>H', packed_data, 6, data.get('coordinate_set', 1))
            struct.pack_into('>l', packed_data, 8, data.get('x_coordinate', 0))
            struct.pack_into('>l', packed_data, 12, data.get('y_coordinate', 0))
            struct.pack_into('>l', packed_data, 16, data.get('z_coordinate', 0))
            struct.pack_into('>h', packed_data, 20, data.get('rx_rotation', 0))
            struct.pack_into('>h', packed_data, 22, data.get('ry_rotation', 0))
            struct.pack_into('>h', packed_data, 24, data.get('rz_rotation', 0))
            struct.pack_into('>H', packed_data, 26, data.get('gripper_status', 0))
            struct.pack_into('>H', packed_data, 28, data.get('speed_override', 50))
            struct.pack_into('>H', packed_data, 30, data.get('motion_type', 1))
            struct.pack_into('>H', packed_data, 32, data.get('precision', 1))
            
            # Add timestamp
            timestamp = int(time.time())
            struct.pack_into('>L', packed_data, 34, timestamp >> 32)
            struct.pack_into('>L', packed_data, 38, timestamp & 0xFFFFFFFF)
            
            struct.pack_into('>H', packed_data, 42, data.get('error_code', 0))
            
            # Write to PLC
            self.client.db_write(self.DB100_NUMBER, 0, packed_data)
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing DB100: {e}")
            return False
    
    def read_db101(self) -> Dict[str, Any]:
        """
        Read DB101 - Robot Interface
        
        Returns:
            dict: DB101 data structure
        """
        if not self.connected:
            raise Exception("Not connected to PLC")
        
        try:
            # Read 100 bytes from DB101
            data = self.client.db_read(self.DB101_NUMBER, 0, 100)
            
            # Unpack data according to DB101 structure
            result = {
                'robot_command': struct.unpack('>H', data[0:2])[0],
                'robot_status': struct.unpack('>H', data[2:4])[0],
                'current_area': struct.unpack('>H', data[4:6])[0],
                'current_set': struct.unpack('>H', data[6:8])[0],
                'current_x': struct.unpack('>l', data[8:12])[0],
                'current_y': struct.unpack('>l', data[12:16])[0],
                'current_z': struct.unpack('>l', data[16:20])[0],
                'current_rx': struct.unpack('>h', data[20:22])[0],
                'current_ry': struct.unpack('>h', data[22:24])[0],
                'current_rz': struct.unpack('>h', data[24:26])[0],
                'motion_status': struct.unpack('>H', data[26:28])[0],
                'gripper_feedback': struct.unpack('>H', data[28:30])[0],
                'current_speed': struct.unpack('>H', data[30:32])[0],
                'path_progress': struct.unpack('>H', data[32:34])[0],
                'execution_time': struct.unpack('>L', data[34:38])[0],
                'robot_error_code': struct.unpack('>H', data[38:40])[0],
                'feedback_timestamp': struct.unpack('>L', data[40:44])[0]
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error reading DB101: {e}")
            raise
    
    def send_command(self, command: str, **kwargs) -> bool:
        """
        Send command to PLC
        
        Args:
            command: Command name from COMMANDS dict
            **kwargs: Additional parameters
            
        Returns:
            bool: True if command sent successfully
        """
        if command not in self.COMMANDS:
            raise ValueError(f"Unknown command: {command}")
        
        command_data = {
            'command_word': self.COMMANDS[command],
            'area_selection': kwargs.get('area', 1),
            'coordinate_set': kwargs.get('set_number', 1),
            'x_coordinate': kwargs.get('x', 0),
            'y_coordinate': kwargs.get('y', 0),
            'z_coordinate': kwargs.get('z', 0),
            'rx_rotation': kwargs.get('rx', 0),
            'ry_rotation': kwargs.get('ry', 0),
            'rz_rotation': kwargs.get('rz', 0),
            'gripper_status': kwargs.get('gripper', 0),
            'speed_override': kwargs.get('speed', 50)
        }
        
        return self.write_db100(command_data)
    
    def wait_for_completion(self, timeout: float = 30.0) -> Tuple[bool, str]:
        """
        Wait for command completion
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            tuple: (success, status_message)
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                db100 = self.read_db100()
                status = db100['status_word']
                
                if status == 3:  # COMPLETED
                    return True, "Command completed successfully"
                elif status == 4:  # ERROR
                    error_code = db100['error_code']
                    return False, f"Command failed with error code: {error_code}"
                elif status == 9:  # VALIDATION_FAILED
                    error_code = db100['error_code']
                    return False, f"Data validation failed: {error_code}"
                elif status == 10:  # TIMEOUT
                    return False, "Command timed out"
                
                time.sleep(0.1)  # Wait 100ms before next check
                
            except Exception as e:
                self.logger.error(f"Error waiting for completion: {e}")
                return False, f"Communication error: {e}"
        
        return False, "Wait timeout"
    
    def write_coordinate_set(self, area: int, set_number: int, x: int, y: int, z: int, 
                           rx: int = 0, ry: int = 0, rz: int = 0, 
                           gripper: int = 0, speed: int = 50) -> bool:
        """
        Write coordinate set to PLC
        
        Args:
            area: Area number (1 or 2)
            set_number: Set number (1-10)
            x, y, z: Coordinates in mm
            rx, ry, rz: Rotations in degrees*100
            gripper: Gripper command (0=open, 1=close)
            speed: Speed override (10-100%)
            
        Returns:
            bool: True if successful
        """
        success = self.send_command('WRITE_COORDINATE', 
                                  area=area, set_number=set_number,
                                  x=x, y=y, z=z, rx=rx, ry=ry, rz=rz,
                                  gripper=gripper, speed=speed)
        
        if success:
            success, message = self.wait_for_completion()
            if success:
                self.logger.info(f"Coordinate set {set_number} written successfully to area {area}")
            else:
                self.logger.error(f"Failed to write coordinate set: {message}")
        
        return success
    
    def execute_coordinate_set(self, area: int, set_number: int) -> bool:
        """
        Execute coordinate set
        
        Args:
            area: Area number (1 or 2)
            set_number: Set number (1-10)
            
        Returns:
            bool: True if successful
        """
        success = self.send_command('EXECUTE_COORDINATE', 
                                  area=area, set_number=set_number)
        
        if success:
            success, message = self.wait_for_completion(timeout=60.0)  # Longer timeout for motion
            if success:
                self.logger.info(f"Coordinate set {set_number} executed successfully in area {area}")
            else:
                self.logger.error(f"Failed to execute coordinate set: {message}")
        
        return success
    
    def get_current_position(self) -> Optional[Dict[str, Any]]:
        """
        Get current robot position
        
        Returns:
            dict: Current position data or None if failed
        """
        success = self.send_command('GET_POSITION')
        
        if success:
            success, message = self.wait_for_completion()
            if success:
                db100 = self.read_db100()
                return {
                    'x': db100['x_coordinate'],
                    'y': db100['y_coordinate'],
                    'z': db100['z_coordinate'],
                    'rx': db100['rx_rotation'],
                    'ry': db100['ry_rotation'],
                    'rz': db100['rz_rotation'],
                    'gripper': db100['gripper_status']
                }
            else:
                self.logger.error(f"Failed to get current position: {message}")
        
        return None
    
    def emergency_stop(self) -> bool:
        """
        Send emergency stop command
        
        Returns:
            bool: True if command sent successfully
        """
        return self.send_command('EMERGENCY_STOP')
    
    def reset_error(self) -> bool:
        """
        Reset error state
        
        Returns:
            bool: True if successful
        """
        success = self.send_command('RESET_ERROR')
        
        if success:
            success, message = self.wait_for_completion()
            if success:
                self.logger.info("Error reset successful")
            else:
                self.logger.error(f"Failed to reset error: {message}")
        
        return success

# Example usage
if __name__ == "__main__":
    # Create PLC client
    plc = PLCClient("192.168.1.100")
    
    try:
        # Connect to PLC
        if plc.connect():
            # Example: Write a coordinate set
            success = plc.write_coordinate_set(
                area=1, set_number=1,
                x=1000, y=500, z=300,
                rx=0, ry=0, rz=0,
                gripper=1, speed=75
            )
            
            if success:
                print("Coordinate set written successfully")
                
                # Execute the coordinate set
                success = plc.execute_coordinate_set(area=1, set_number=1)
                
                if success:
                    print("Coordinate set executed successfully")
                else:
                    print("Failed to execute coordinate set")
            else:
                print("Failed to write coordinate set")
                
        else:
            print("Failed to connect to PLC")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        plc.disconnect()
