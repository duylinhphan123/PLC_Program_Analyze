# PC-PLC-Robot Communication System - Installation Guide

## System Overview

This installation guide provides step-by-step instructions for setting up the PC-PLC-Robot communication system for coordinate exchange between a laptop, Siemens S7-400H PLC, and ABB robot controller.

## System Requirements

### Hardware Requirements

#### PLC System
- **CPU**: Siemens CPU 412-3H (S7-400H system)
- **Communication Module**: CP 443-1 (Ethernet) or PROFIBUS-DP master
- **Memory**: Minimum 1.5 MB work memory, 8 MB load memory
- **I/O Modules**: As per application requirements

#### Robot System
- **Robot**: ABB IRB 2600 (or compatible)
- **Controller**: IRC5 with RobotWare 6.08 or higher
- **Communication**: PROFIBUS-DP or Ethernet interface
- **Software**: RAPID programming environment

#### Laptop/PC System
- **OS**: Windows 10/11 (64-bit) or Linux Ubuntu 18.04+
- **Memory**: Minimum 8 GB RAM
- **Storage**: 500 GB available space
- **Network**: Ethernet interface (1 Gbps recommended)

### Software Requirements

#### PLC Programming
- **STEP 7**: V5.6 or TIA Portal V16+
- **WinCC**: Optional for HMI
- **S7-PLCSIM**: For simulation and testing

#### Robot Programming
- **RobotStudio**: 2021.1 or higher
- **RAPID**: Programming environment
- **FlexPendant**: For teaching and testing

#### Laptop/PC Software
- **Python**: 3.8 or higher
- **Required Python packages**:
  - python-snap7
  - tkinter (usually included)
  - json
  - threading
  - numpy (optional)

## Network Configuration

### IP Address Assignment

```
Device          IP Address      Subnet Mask     Gateway
------------------------------------------------------
PLC CPU         192.168.1.100   255.255.255.0   192.168.1.1
Robot Controller 192.168.1.20    255.255.255.0   192.168.1.1
Laptop/PC       192.168.1.10    255.255.255.0   192.168.1.1
Network Switch  192.168.1.1     255.255.255.0   -
```

### Port Configuration

- **S7 Communication**: Port 102 (TCP)
- **PROFIBUS-DP**: According to PROFIBUS configuration
- **HTTP/Web**: Port 80 (optional)
- **OPC UA**: Port 4840 (optional)

## Installation Steps

### Step 1: PLC System Setup

#### 1.1 Hardware Installation
1. Install CPU 412-3H in S7-400H rack
2. Install communication module (CP 443-1 or PROFIBUS-DP master)
3. Connect power supply and verify LED status
4. Connect Ethernet cable to CP 443-1 or PROFIBUS cable to DP master

#### 1.2 Software Installation
1. Install STEP 7 or TIA Portal on programming PC
2. Create new project for CPU 412-3H
3. Configure hardware (CPU, communication modules, I/O)
4. Set IP address for CP 443-1 (192.168.1.100)

#### 1.3 Program Upload
1. Open STEP 7/TIA Portal project
2. Import AWL files from `plc_code` directory:
   - `DB100_LaptopInterface.awl`
   - `DB101_RobotInterface.awl`
   - `DB102_CoordinateStorage.awl`
   - `FC300_LaptopHandler.awl`
   - `FC301_RobotHandler.awl`
   - `FC302_CoordinateManager.awl`
   - `FC303_DataValidator.awl`
   - `OB_Integration.awl`
3. Compile and download to PLC
4. Verify no compilation errors

### Step 2: Robot System Setup

#### 2.1 Hardware Installation
1. Ensure robot controller is properly installed and powered
2. Connect communication interface (PROFIBUS-DP or Ethernet)
3. Verify robot calibration and safety systems

#### 2.2 Software Installation
1. Install RobotStudio on programming PC
2. Connect to robot controller
3. Backup existing robot program

#### 2.3 Program Upload
1. Open RobotStudio and connect to robot
2. Import RAPID modules from `robot_code` directory:
   - `PLC_Interface.mod`
   - `Coordinate_Handler.mod`
3. Configure I/O signals for gripper control
4. Verify program syntax and load to controller
5. Test basic robot movements

### Step 3: Laptop/PC Setup

#### 3.1 Python Environment
1. Install Python 3.8 or higher
2. Create virtual environment:
   ```bash
   python -m venv plc_robot_env
   source plc_robot_env/bin/activate  # Linux/Mac
   plc_robot_env\Scripts\activate     # Windows
   ```

#### 3.2 Install Dependencies
```bash
pip install python-snap7
pip install tkinter
pip install numpy
```

#### 3.3 Install Snap7 Library
**Windows:**
1. Download Snap7 library from official website
2. Extract to `C:\snap7\bin\`
3. Add to system PATH

**Linux:**
```bash
sudo apt-get install libsnap7-1
sudo apt-get install libsnap7-dev
```

#### 3.4 Application Setup
1. Copy `laptop_code` directory to laptop
2. Copy `config` directory to laptop
3. Modify configuration files as needed:
   - `system_config.json`: System parameters
   - `network_config.json`: Network settings

### Step 4: Network Configuration

#### 4.1 PLC Network Setup
1. Access PLC via STEP 7/TIA Portal
2. Configure CP 443-1 Ethernet interface:
   - IP: 192.168.1.100
   - Subnet: 255.255.255.0
   - Gateway: 192.168.1.1
3. Enable S7 communication
4. Test connectivity with ping

#### 4.2 Robot Network Setup
1. Access robot controller via FlexPendant
2. Configure network settings:
   - IP: 192.168.1.20
   - Subnet: 255.255.255.0
   - Gateway: 192.168.1.1
3. Test connectivity with ping

#### 4.3 Laptop Network Setup
1. Configure network adapter:
   - IP: 192.168.1.10
   - Subnet: 255.255.255.0
   - Gateway: 192.168.1.1
2. Test connectivity to PLC and robot

### Step 5: System Integration

#### 5.1 Communication Testing
1. Test PLC-Laptop communication:
   ```python
   python laptop_code/plc_client.py
   ```
2. Test robot communication manually
3. Verify data exchange between all components

#### 5.2 Coordinate System Calibration
1. Define coordinate systems for each area
2. Calibrate robot tool center point (TCP)
3. Teach reference positions
4. Verify coordinate transformations

#### 5.3 Safety Configuration
1. Configure safety zones in robot program
2. Set up emergency stop procedures
3. Test safety interlocks
4. Verify collision detection

## Configuration Files

### System Configuration
Edit `config/system_config.json`:
- PLC IP address and connection parameters
- Coordinate limits for each area
- Safety parameters
- Command and status codes

### Network Configuration
Edit `config/network_config.json`:
- Network topology
- Device IP addresses
- Communication protocols
- Security settings

### Validation Configuration
The system automatically creates validation rules based on:
- Robot workspace limits
- Safety zones
- Motion constraints
- Speed limits

## Testing Procedures

### 1. Communication Test
```python
# Test PLC communication
python -c "
from laptop_code.plc_client import PLCClient
plc = PLCClient('192.168.1.100')
if plc.connect():
    print('PLC connection successful')
    plc.disconnect()
else:
    print('PLC connection failed')
"
```

### 2. Coordinate Validation Test
```python
# Test coordinate validation
python -c "
from laptop_code.data_validator import DataValidator
validator = DataValidator()
result = validator.validate_coordinate(1000, 500, 300, area=1)
print(f'Validation result: {result.is_valid}')
if not result.is_valid:
    for error in result.errors:
        print(f'Error: {error.message}')
"
```

### 3. End-to-End Test
1. Start robot program
2. Launch GUI application:
   ```python
   python laptop_code/gui_interface.py
   ```
3. Connect to PLC
4. Create test coordinate set
5. Execute coordinate movement
6. Verify robot reaches target position

## Troubleshooting

### Common Issues

#### 1. PLC Connection Failed
- **Symptom**: Cannot connect to PLC
- **Solutions**:
  - Check network connectivity (ping 192.168.1.100)
  - Verify PLC IP configuration
  - Check firewall settings
  - Ensure CP 443-1 module is configured correctly

#### 2. Robot Communication Error
- **Symptom**: Robot not responding to commands
- **Solutions**:
  - Check robot controller status
  - Verify RAPID program is running
  - Check I/O signal configuration
  - Ensure robot is in automatic mode

#### 3. Coordinate Validation Errors
- **Symptom**: Coordinates rejected by validation
- **Solutions**:
  - Check coordinate limits in configuration
  - Verify robot workspace limits
  - Check safety zone definitions
  - Ensure coordinates are within reach

#### 4. GUI Application Issues
- **Symptom**: GUI not starting or crashing
- **Solutions**:
  - Check Python environment
  - Verify all dependencies installed
  - Check configuration file syntax
  - Review error logs

### Diagnostic Tools

#### 1. PLC Diagnostics
- Use STEP 7/TIA Portal diagnostics
- Check CPU load and memory usage
- Monitor communication status
- Review system logs

#### 2. Robot Diagnostics
- Use FlexPendant diagnostics
- Check robot status and error logs
- Monitor I/O signals
- Verify program execution

#### 3. Network Diagnostics
- Use ping and traceroute
- Check switch status and configuration
- Monitor network traffic
- Verify cable connections

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Check system status
- Review error logs
- Verify communication status
- Test emergency stop

#### Weekly
- Backup coordinate sets
- Check robot calibration
- Review performance metrics
- Update documentation

#### Monthly
- Full system backup
- Software updates
- Hardware inspection
- Performance optimization

### Backup Procedures

#### 1. PLC Backup
- Use STEP 7/TIA Portal backup function
- Save to network location
- Include program, configuration, and data

#### 2. Robot Backup
- Use RobotStudio backup function
- Save RAPID programs and configuration
- Include calibration data

#### 3. Laptop Backup
- Backup coordinate sets and configuration
- Save user data and logs
- Create system restore point

## Support and Documentation

### Technical Support
- PLC: Siemens technical support
- Robot: ABB robotics support
- Software: Internal development team

### Documentation
- System architecture diagrams
- Network topology
- Program documentation
- User manuals

### Training
- Operator training materials
- Maintenance procedures
- Emergency procedures
- Safety protocols

## Appendices

### Appendix A: Error Codes
See `config/system_config.json` for complete error code definitions.

### Appendix B: Network Diagrams
Network topology diagrams available in `documentation/network_diagrams/`.

### Appendix C: Safety Documentation
Safety procedures and risk assessment in `documentation/safety/`.

### Appendix D: Validation Rules
Complete validation rules in `config/validation_config.json`.

---

**Document Version**: 1.0  
**Date**: 17/07/2025  
**Author**: PLC Programming Team  
**Approved**: Engineering Manager
