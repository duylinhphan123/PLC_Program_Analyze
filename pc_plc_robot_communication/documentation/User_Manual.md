# PC-PLC-Robot Communication System - User Manual

## Table of Contents
1. [System Overview](#system-overview)
2. [Getting Started](#getting-started)
3. [GUI Interface](#gui-interface)
4. [Coordinate Management](#coordinate-management)
5. [Robot Control](#robot-control)
6. [Monitoring and Diagnostics](#monitoring-and-diagnostics)
7. [Safety Procedures](#safety-procedures)
8. [Troubleshooting](#troubleshooting)
9. [Appendices](#appendices)

## System Overview

### Purpose
The PC-PLC-Robot Communication System enables coordinate exchange between a laptop computer, Siemens S7-400H PLC, and ABB robot controller for automated palletizing operations.

### Key Features
- **Coordinate Management**: Store and manage coordinate sets for different areas
- **Real-time Communication**: Seamless data exchange between laptop, PLC, and robot
- **Safety Monitoring**: Comprehensive safety checks and validation
- **User-friendly Interface**: Intuitive GUI for easy operation
- **Data Validation**: Automatic validation of coordinates and parameters
- **Error Handling**: Comprehensive error detection and reporting

### System Components
- **Laptop Application**: Python-based GUI for coordinate management
- **PLC Program**: AWL program for communication and coordination
- **Robot Program**: RAPID modules for motion control
- **Configuration System**: JSON-based configuration management

## Getting Started

### Prerequisites
Before using the system, ensure:
- All hardware components are properly installed
- Network connectivity is established
- PLC and robot programs are loaded and running
- Laptop application is properly configured

### Starting the System

#### 1. Start PLC System
1. Power on S7-400H PLC system
2. Wait for CPU to reach RUN state
3. Verify communication module status

#### 2. Start Robot System
1. Power on robot controller
2. Start robot program using FlexPendant
3. Verify robot is in automatic mode
4. Check safety systems are active

#### 3. Start Laptop Application
1. Navigate to application directory
2. Run the GUI application:
   ```bash
   python laptop_code/gui_interface.py
   ```
3. The main window will open

### Initial Configuration
1. Open the **Connection** tab
2. Verify PLC IP address (default: 192.168.1.100)
3. Click **Connect** to establish PLC connection
4. Wait for connection confirmation

## GUI Interface

### Main Window Layout
The GUI consists of five main tabs:
- **Connection**: PLC connection management
- **Coordinates**: Coordinate input and management
- **Control**: Robot control and execution
- **Monitor**: System monitoring and status
- **Configuration**: System configuration and file operations

### Connection Tab

#### PLC Connection Settings
- **PLC IP Address**: IP address of the PLC (default: 192.168.1.100)
- **Rack**: PLC rack number (default: 0)
- **Slot**: PLC slot number (default: 2)

#### Connection Controls
- **Connect**: Establish connection to PLC
- **Disconnect**: Disconnect from PLC

#### Connection Status
- **Status**: Current connection status
- **Last Update**: Timestamp of last communication

### Coordinates Tab

#### Area and Set Selection
- **Area**: Select working area (1 or 2)
- **Set**: Select coordinate set (1-10)

#### Coordinate Input
- **Position**: X, Y, Z coordinates in millimeters
- **Rotation**: RX, RY, RZ rotations in degrees
- **Gripper**: Gripper command (0=open, 1=close)
- **Speed**: Speed override (10-100%)

#### Coordinate Management
- **Validate**: Validate current coordinate input
- **Save Set**: Save coordinate as a set
- **Load Set**: Load coordinate set from memory
- **Get Current**: Retrieve current robot position

#### Coordinate Sets List
Displays all saved coordinate sets with:
- Area number
- Set number
- X, Y, Z coordinates
- Description

### Control Tab

#### Execution Controls
- **Write to PLC**: Send coordinate to PLC
- **Execute Set**: Execute coordinate movement
- **Get Position**: Retrieve current robot position

#### Emergency Controls
- **EMERGENCY STOP**: Immediately stop all robot motion
- **Reset Error**: Clear error conditions
- **Stop Motion**: Stop current motion

#### Current Position Display
Shows current robot position in real-time

#### Operation Log
Displays system messages and operation history

### Monitor Tab

#### Monitoring Controls
- **Start/Stop Monitoring**: Enable/disable real-time monitoring
- **Refresh**: Update status displays

#### System Status
- **PLC Status**: Current PLC connection status
- **Robot Status**: Current robot operational status

#### Data Blocks Display
Real-time display of PLC data blocks:
- **DB100**: Laptop interface data
- **DB101**: Robot interface data

### Configuration Tab

#### File Operations
- **Import CSV**: Import coordinates from CSV file
- **Export CSV**: Export coordinates to CSV file
- **Save Config**: Save current configuration
- **Load Config**: Load configuration from file

#### System Information
Displays system version, configuration, and status information

## Coordinate Management

### Coordinate Systems

#### Global Coordinate System
- **Origin**: Robot base coordinate system
- **X-axis**: Forward direction
- **Y-axis**: Left direction
- **Z-axis**: Upward direction

#### Area Coordinate Systems
- **Area 1**: Palletizing area 1 (left side)
- **Area 2**: Palletizing area 2 (right side)

### Coordinate Limits

#### Area 1 Limits
- **X Range**: -1500 to 1500 mm
- **Y Range**: -1500 to 1500 mm  
- **Z Range**: 100 to 800 mm

#### Area 2 Limits
- **X Range**: -1500 to 1500 mm
- **Y Range**: -1500 to 1500 mm
- **Z Range**: 100 to 800 mm

### Creating Coordinate Sets

#### Manual Input
1. Select area and set number
2. Enter coordinate values
3. Set gripper command and speed
4. Click **Validate** to check coordinate
5. Click **Save Set** to store coordinate

#### Teaching Method
1. Move robot to desired position manually
2. Click **Get Current** to retrieve position
3. Modify coordinates if needed
4. Click **Save Set** to store coordinate

#### CSV Import
1. Prepare CSV file with coordinate data
2. Click **Import CSV** in Configuration tab
3. Select file and confirm import
4. Verify imported coordinates

### Coordinate Validation

#### Automatic Validation
The system automatically validates:
- Coordinate ranges
- Robot reachability
- Safety zone compliance
- Motion constraints

#### Validation Results
- **Valid**: Coordinate passes all checks
- **Warning**: Coordinate passes but has warnings
- **Error**: Coordinate fails validation

#### Common Validation Errors
- Coordinate out of range
- Target not reachable
- Safety zone violation
- Invalid parameter values

## Robot Control

### Motion Types

#### Linear Motion
- **Description**: Straight-line motion to target
- **Use Case**: Precision positioning
- **Speed**: Controlled by speed override

#### Joint Motion
- **Description**: Joint-space motion to target
- **Use Case**: Fast positioning
- **Speed**: Controlled by speed override

### Speed Control

#### Speed Override
- **Range**: 10-100%
- **Default**: 50%
- **Recommendation**: Start with low speed for testing

#### Speed Considerations
- **Low Speed (10-30%)**: Testing and precision work
- **Medium Speed (30-70%)**: Normal operation
- **High Speed (70-100%)**: Production mode

### Gripper Control

#### Gripper Commands
- **0**: Open gripper
- **1**: Close gripper

#### Gripper Safety
- Always ensure gripper is in correct state before motion
- Check gripper feedback after command

### Motion Execution

#### Single Coordinate
1. Select area and set number
2. Ensure coordinate is valid
3. Click **Execute Set**
4. Monitor motion progress
5. Verify completion

#### Sequence Execution
1. Create multiple coordinate sets
2. Use sequence execution features
3. Monitor each step
4. Handle any errors

### Safety Features

#### Emergency Stop
- **Function**: Immediately stops all motion
- **Activation**: Click red EMERGENCY STOP button
- **Recovery**: Reset error and restart

#### Safety Zones
- **Definition**: Restricted areas for robot motion
- **Enforcement**: Automatic collision checking
- **Override**: Not permitted for safety

#### Motion Limits
- **Workspace**: Robot motion limited to defined workspace
- **Speed**: Maximum speed limits enforced
- **Acceleration**: Controlled acceleration/deceleration

## Monitoring and Diagnostics

### Real-time Monitoring

#### System Status
- **PLC Status**: Communication and operational status
- **Robot Status**: Motion and error status
- **Network Status**: Communication quality

#### Data Monitoring
- **Position**: Current robot position
- **Speed**: Current motion speed
- **Errors**: Active error conditions

### Performance Metrics

#### Communication
- **Response Time**: PLC communication latency
- **Error Rate**: Communication error frequency
- **Throughput**: Data transfer rate

#### Motion
- **Execution Time**: Time to complete motion
- **Accuracy**: Position accuracy
- **Repeatability**: Motion consistency

### Diagnostic Tools

#### Error Logs
- **Location**: Operation log in Control tab
- **Content**: Error messages and timestamps
- **Analysis**: Error pattern identification

#### System Information
- **Hardware**: PLC and robot status
- **Software**: Version information
- **Configuration**: Current settings

### Troubleshooting

#### Communication Issues
1. Check network connectivity
2. Verify PLC status
3. Restart communication
4. Check configuration

#### Motion Issues
1. Check robot status
2. Verify coordinate validity
3. Check safety systems
4. Review error messages

#### Performance Issues
1. Monitor system load
2. Check network traffic
3. Optimize coordinate sets
4. Review motion parameters

## Safety Procedures

### General Safety Rules

#### Before Operation
1. Verify all safety systems are active
2. Check emergency stop functions
3. Ensure work area is clear
4. Confirm proper PPE is worn

#### During Operation
1. Monitor robot motion continuously
2. Be ready to activate emergency stop
3. Maintain safe distance from robot
4. Follow lockout/tagout procedures

#### After Operation
1. Return robot to safe position
2. Disconnect from PLC
3. Secure work area
4. Complete operation log

### Emergency Procedures

#### Emergency Stop Activation
1. Press emergency stop button immediately
2. Verify robot motion has stopped
3. Assess situation for safety
4. Follow recovery procedures

#### Error Recovery
1. Identify error cause
2. Clear error conditions
3. Reset robot system
4. Verify safety before restart

#### System Malfunction
1. Stop all operations immediately
2. Disconnect power if necessary
3. Contact technical support
4. Document incident

### Safety Zones

#### Defined Safety Zones
- **Conveyor Zone**: Conveyor belt area
- **Fixture Zone**: Fixture and tooling area
- **Maintenance Zone**: Service access area

#### Safety Zone Enforcement
- Automatic collision checking
- Motion prevention in restricted areas
- Warning messages for violations

### Risk Assessment

#### High-Risk Operations
- High-speed motion
- Heavy payload handling
- Complex coordinate sequences
- Maintenance activities

#### Risk Mitigation
- Reduced speed for testing
- Proper training for operators
- Regular safety inspections
- Emergency procedure training

## Troubleshooting

### Common Issues and Solutions

#### Connection Problems

**Issue**: Cannot connect to PLC
**Symptoms**: Connection failed error message
**Solutions**:
1. Check network cable connections
2. Verify PLC IP address
3. Check firewall settings
4. Restart PLC communication module

**Issue**: Intermittent connection loss
**Symptoms**: Frequent disconnections
**Solutions**:
1. Check network stability
2. Verify cable integrity
3. Reduce communication frequency
4. Check for network interference

#### Coordinate Issues

**Issue**: Coordinate validation failed
**Symptoms**: Red error message in validation
**Solutions**:
1. Check coordinate ranges
2. Verify area selection
3. Ensure robot reachability
4. Check safety zone compliance

**Issue**: Robot motion inaccurate
**Symptoms**: Robot doesn't reach target position
**Solutions**:
1. Check robot calibration
2. Verify coordinate system
3. Check tool center point
4. Perform robot calibration

#### Motion Problems

**Issue**: Robot not moving
**Symptoms**: Execute command has no effect
**Solutions**:
1. Check robot status
2. Verify robot mode (automatic)
3. Check safety systems
4. Reset error conditions

**Issue**: Motion too slow/fast
**Symptoms**: Unexpected motion speed
**Solutions**:
1. Check speed override setting
2. Verify robot speed limits
3. Check motion type selection
4. Adjust speed parameters

#### GUI Issues

**Issue**: GUI not responding
**Symptoms**: Interface freezes or crashes
**Solutions**:
1. Restart application
2. Check system resources
3. Verify Python environment
4. Review error logs

**Issue**: Data not updating
**Symptoms**: Static display values
**Solutions**:
1. Check monitoring status
2. Verify PLC connection
3. Restart monitoring
4. Check update intervals

### Error Codes

#### Communication Errors (1000-1999)
- **1001**: PLC connection timeout
- **1002**: Invalid response from PLC
- **1003**: Network communication error
- **1004**: Protocol error

#### Coordinate Errors (2000-2999)
- **2001**: Coordinate out of range
- **2002**: Target not reachable
- **2003**: Safety zone violation
- **2004**: Invalid parameter value

#### Motion Errors (3000-3999)
- **3001**: Robot not ready
- **3002**: Motion timeout
- **3003**: Path planning error
- **3004**: Collision detected

#### System Errors (4000-4999)
- **4001**: System initialization failed
- **4002**: Configuration error
- **4003**: Resource allocation error
- **4004**: Internal system error

### Diagnostic Procedures

#### Communication Diagnostics
1. Test network connectivity (ping)
2. Check PLC status in STEP 7
3. Verify communication module
4. Monitor network traffic

#### Robot Diagnostics
1. Check robot controller status
2. Verify program execution
3. Test manual motion
4. Check I/O signals

#### System Diagnostics
1. Review system logs
2. Check performance metrics
3. Verify configuration files
4. Test individual components

### Support Contacts

#### Technical Support
- **PLC Issues**: Siemens technical support
- **Robot Issues**: ABB robotics support
- **Software Issues**: Internal development team

#### Emergency Contacts
- **Safety Issues**: Plant safety officer
- **System Down**: Production supervisor
- **Maintenance**: Maintenance department

## Appendices

### Appendix A: Coordinate Examples

#### Example Coordinate Sets
```
Area 1, Set 1: Pallet Position 1
X: 800, Y: -600, Z: 400
RX: 0, RY: 0, RZ: 0
Gripper: 1, Speed: 50%

Area 1, Set 2: Pallet Position 2
X: 800, Y: -600, Z: 600
RX: 0, RY: 0, RZ: 0
Gripper: 0, Speed: 50%
```

### Appendix B: CSV File Format

#### Import Format
```csv
area,set_number,x,y,z,rx,ry,rz,gripper,speed,description
1,1,800,-600,400,0,0,0,1,50,"Pallet Position 1"
1,2,800,-600,600,0,0,0,0,50,"Pallet Position 2"
```

### Appendix C: Configuration Examples

#### System Configuration
See `config/system_config.json` for complete configuration options.

#### Network Configuration
See `config/network_config.json` for network setup details.

### Appendix D: Keyboard Shortcuts

#### GUI Shortcuts
- **Ctrl+C**: Connect to PLC
- **Ctrl+D**: Disconnect from PLC
- **Ctrl+S**: Save coordinate set
- **Ctrl+L**: Load coordinate set
- **F5**: Refresh status
- **Esc**: Emergency stop

---

**Document Version**: 1.0  
**Date**: 17/07/2025  
**Author**: PLC Programming Team  
**Last Updated**: 17/07/2025
