# PC-PLC-Robot Communication System

## Overview

This system provides a comprehensive solution for coordinate exchange between a laptop computer, Siemens S7-400H PLC, and ABB robot controller for automated palletizing operations. The system enables seamless communication and coordination between all three components while maintaining safety and reliability.

## Key Features

- **Real-time Communication**: Seamless data exchange between laptop, PLC, and robot
- **Coordinate Management**: Store and manage coordinate sets for different palletizing areas
- **Safety Monitoring**: Comprehensive safety checks and validation
- **User-friendly Interface**: Intuitive GUI for easy operation
- **Data Validation**: Automatic validation of coordinates and parameters
- **Error Handling**: Comprehensive error detection and reporting
- **Scalable Architecture**: Modular design for easy expansion

## System Architecture

```
┌─────────────────┐    Ethernet/S7     ┌─────────────────┐    PROFIBUS-DP    ┌─────────────────┐
│   Laptop PC     │◄──────────────────►│  Siemens PLC    │◄─────────────────►│   ABB Robot     │
│                 │                    │   S7-400H       │                   │   Controller    │
│ - GUI Interface │                    │                 │                   │                 │
│ - Coordinate Mgr│                    │ - Communication │                   │ - Motion Control│
│ - Data Validator│                    │ - Coordination  │                   │ - Safety Logic  │
│ - PLC Client    │                    │ - Data Storage  │                   │ - I/O Handling  │
└─────────────────┘                    └─────────────────┘                   └─────────────────┘
```

## Directory Structure

```
pc_plc_robot_communication/
├── plc_code/                      # PLC AWL programs
│   ├── DB100_LaptopInterface.awl
│   ├── DB101_RobotInterface.awl
│   ├── DB102_CoordinateStorage.awl
│   ├── FC300_LaptopHandler.awl
│   ├── FC301_RobotHandler.awl
│   ├── FC302_CoordinateManager.awl
│   ├── FC303_DataValidator.awl
│   └── OB_Integration.awl
├── laptop_code/                   # Python applications
│   ├── plc_client.py
│   ├── coordinate_manager.py
│   ├── data_validator.py
│   └── gui_interface.py
├── robot_code/                    # RAPID modules
│   ├── PLC_Interface.mod
│   └── Coordinate_Handler.mod
├── config/                        # Configuration files
│   ├── system_config.json
│   └── network_config.json
└── documentation/                 # Documentation
    ├── Installation_Guide.md
    └── User_Manual.md
```

## Quick Start

### Prerequisites

1. **Hardware**:
   - Siemens S7-400H PLC with CPU 412-3H
   - ABB robot with IRC5 controller
   - Laptop/PC with network connectivity

2. **Software**:
   - STEP 7 or TIA Portal for PLC programming
   - RobotStudio for robot programming
   - Python 3.8+ for laptop application

### Installation

1. **PLC Setup**:
   ```bash
   # Load AWL programs to PLC using STEP 7/TIA Portal
   # Configure network settings (IP: 192.168.1.100)
   ```

2. **Robot Setup**:
   ```bash
   # Load RAPID modules using RobotStudio
   # Configure network settings (IP: 192.168.1.20)
   ```

3. **Laptop Setup**:
   ```bash
   # Install Python dependencies
   pip install python-snap7
   
   # Configure network (IP: 192.168.1.10)
   # Run GUI application
   python laptop_code/gui_interface.py
   ```

### Basic Usage

1. **Connect to PLC**:
   - Open GUI application
   - Navigate to Connection tab
   - Click "Connect" button

2. **Create Coordinate Set**:
   - Go to Coordinates tab
   - Enter coordinate values
   - Click "Validate" then "Save Set"

3. **Execute Motion**:
   - Select area and set number
   - Click "Execute Set"
   - Monitor robot motion

## System Components

### PLC Code (AWL)

#### Data Blocks
- **DB100**: Laptop interface for command and data exchange
- **DB101**: Robot interface for feedback and status
- **DB102**: Coordinate storage for multiple sets

#### Function Blocks
- **FC300**: Laptop handler for processing laptop commands
- **FC301**: Robot handler for robot communication
- **FC302**: Coordinate manager for coordinate operations
- **FC303**: Data validator for input validation

#### Organization Blocks
- **OB Integration**: Integration with existing OB1 and OB35

### Laptop Code (Python)

#### Core Modules
- **plc_client.py**: S7 communication client
- **coordinate_manager.py**: Coordinate set management
- **data_validator.py**: Data validation and safety checks
- **gui_interface.py**: Graphical user interface

#### Features
- Real-time PLC communication
- Coordinate validation and management
- Comprehensive error handling
- User-friendly GUI interface

### Robot Code (RAPID)

#### Modules
- **PLC_Interface.mod**: PLC communication interface
- **Coordinate_Handler.mod**: Coordinate management and validation

#### Features
- PROFIBUS-DP communication
- Motion control and safety
- Coordinate validation
- Error handling

## Configuration

### System Configuration (`config/system_config.json`)

```json
{
  "plc_communication": {
    "ip_address": "192.168.1.100",
    "rack": 0,
    "slot": 2
  },
  "coordinate_limits": {
    "area_1": {
      "x_min": -1500, "x_max": 1500,
      "y_min": -1500, "y_max": 1500,
      "z_min": 100, "z_max": 800
    }
  }
}
```

### Network Configuration (`config/network_config.json`)

```json
{
  "network": {
    "plc_ip": "192.168.1.100",
    "laptop_ip": "192.168.1.10",
    "robot_ip": "192.168.1.20"
  }
}
```

## Safety Features

### Coordinate Validation
- Range checking for X, Y, Z coordinates
- Rotation limit validation
- Reachability analysis
- Safety zone compliance

### Motion Safety
- Emergency stop functionality
- Speed limiting
- Collision detection
- Safety zone enforcement

### Communication Safety
- Connection monitoring
- Timeout handling
- Error recovery
- Data integrity checks

## API Reference

### PLC Client (`plc_client.py`)

```python
from plc_client import PLCClient

# Create client and connect
plc = PLCClient("192.168.1.100")
plc.connect()

# Write coordinate set
plc.write_coordinate_set(
    area=1, set_number=1,
    x=1000, y=500, z=300,
    gripper=1, speed=50
)

# Execute coordinate set
plc.execute_coordinate_set(area=1, set_number=1)

# Get current position
position = plc.get_current_position()
```

### Coordinate Manager (`coordinate_manager.py`)

```python
from coordinate_manager import CoordinateManager, Coordinate, CoordinateSet

# Create coordinate manager
coord_mgr = CoordinateManager(plc_client)

# Create coordinate set
coord = Coordinate(x=1000, y=500, z=300, gripper=1, speed=50)
coord_set = CoordinateSet(area=1, set_number=1, coordinates=[coord])

# Add coordinate set
coord_mgr.add_coordinate_set(coord_set)

# Execute coordinate set
coord_mgr.execute_coordinate_set(area=1, set_number=1)
```

### Data Validator (`data_validator.py`)

```python
from data_validator import DataValidator

# Create validator
validator = DataValidator()

# Validate coordinate
result = validator.validate_coordinate(1000, 500, 300, area=1)
if result.is_valid:
    print("Coordinate is valid")
else:
    for error in result.errors:
        print(f"Error: {error.message}")
```

## Error Handling

### Error Categories

#### Communication Errors (1000-1999)
- PLC connection failures
- Network timeouts
- Protocol errors

#### Coordinate Errors (2000-2999)
- Out of range coordinates
- Reachability issues
- Safety zone violations

#### Motion Errors (3000-3999)
- Robot not ready
- Motion timeouts
- Path planning errors

#### System Errors (4000-4999)
- Initialization failures
- Configuration errors
- Resource allocation issues

### Error Recovery

```python
try:
    plc.execute_coordinate_set(area=1, set_number=1)
except Exception as e:
    print(f"Error: {e}")
    plc.reset_error()  # Reset error state
    # Retry operation
```

## Testing

### Unit Tests

```bash
# Run PLC communication tests
python -m pytest tests/test_plc_client.py

# Run coordinate validation tests
python -m pytest tests/test_data_validator.py

# Run coordinate manager tests
python -m pytest tests/test_coordinate_manager.py
```

### Integration Tests

```bash
# Test complete system integration
python tests/integration_test.py
```

### Example Test

```python
def test_coordinate_validation():
    validator = DataValidator()
    result = validator.validate_coordinate(1000, 500, 300, area=1)
    assert result.is_valid == True
    assert len(result.errors) == 0
```

## Monitoring and Diagnostics

### Performance Metrics
- Communication latency
- Motion execution time
- Error frequency
- System availability

### Diagnostic Tools
- Real-time monitoring
- Error logging
- Performance analysis
- System health checks

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system.log'),
        logging.StreamHandler()
    ]
)
```

## Maintenance

### Regular Tasks
- **Daily**: System status check, error log review
- **Weekly**: Performance analysis, backup verification
- **Monthly**: Software updates, hardware inspection

### Backup Procedures
- PLC program backup
- Coordinate set backup
- Configuration backup
- Log file archival

## Troubleshooting

### Common Issues

#### Cannot Connect to PLC
1. Check network connectivity
2. Verify PLC IP address
3. Check firewall settings
4. Ensure PLC is in RUN mode

#### Coordinate Validation Failed
1. Check coordinate ranges
2. Verify area selection
3. Ensure robot reachability
4. Check safety zone compliance

#### Robot Not Moving
1. Check robot status
2. Verify automatic mode
3. Check safety systems
4. Reset error conditions

## Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/company/pc-plc-robot-communication.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable names
- Include comprehensive comments
- Write unit tests for new features

### Submission Guidelines
1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Update documentation
6. Submit pull request

## Support

### Documentation
- [Installation Guide](documentation/Installation_Guide.md)
- [User Manual](documentation/User_Manual.md)
- [API Reference](documentation/API_Reference.md)

### Technical Support
- **PLC Issues**: Siemens technical support
- **Robot Issues**: ABB robotics support
- **Software Issues**: Internal development team

### Community
- Issue tracking: GitHub Issues
- Discussions: GitHub Discussions
- Wiki: Project Wiki

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.0 (2025-07-17)
- Initial release
- PLC communication system
- Robot interface
- GUI application
- Coordinate management
- Safety features
- Documentation

## Acknowledgments

- Siemens for S7 communication protocols
- ABB for robot integration support
- Python community for excellent libraries
- Development team for their contributions

---

**Project**: PC-PLC-Robot Communication System  
**Version**: 1.0  
**Date**: 17/07/2025  
**Status**: Production Ready  
**Maintainer**: PLC Programming Team
3. No modification to existing program required

### Laptop Side
1. Install Python 3.8+ and required packages
2. Configure network settings
3. Run `plc_client.py` for basic communication
4. Run `gui_interface.py` for GUI application

### Robot Side
1. Load RAPID modules from `robot_code/` folder
2. Configure I/O mappings
3. Start coordinate handler task

---

## 🔗 PROTOCOL OVERVIEW

### Data Flow
```
Laptop → PLC DB100 → PLC Logic → PLC DB101 → Robot
  ↑                                           ↓
  ←─────────── Status/Feedback ←─────────────
```

### Communication Cycle
1. Laptop writes coordinate data to PLC DB100
2. PLC validates and processes data
3. PLC sends commands to Robot via DB101
4. Robot executes and sends feedback
5. PLC updates status to Laptop

---

## 📊 DATA STRUCTURES

### DB100 - Laptop Interface (50 words)
- Command/Status handshake
- Coordinate data (X,Y,Z,RX,RY,RZ)
- Area selection and set numbers
- Error handling and timestamps

### DB101 - Robot Interface (50 words)
- Robot command/status handshake
- Current position feedback
- Motion status and error codes
- Execution timing data

### DB102 - Coordinate Storage (500 words)
- 10 coordinate sets per area (2 areas)
- Validation flags and checksums
- Historical data storage

---

## 🛡️ SAFETY FEATURES

- Independent operation from main program
- Data validation and range checking
- Error handling and recovery
- Timeout protection
- Manual override capabilities

---

## 📋 INTEGRATION REQUIREMENTS

### Minimal Integration
- Add function calls to existing OB1 or OB35
- No modification to existing logic
- Independent error handling
- Separate diagnostic interface

### Network Requirements
- Ethernet connection for Laptop-PLC
- PROFIBUS-DP for PLC-Robot (existing)
- IP configuration per network_config.json

---

**Status:** Ready for implementation  
**Compatibility:** S7-400H CPU 412-3H + ABB IRC5  
**Dependencies:** None (standalone system)
