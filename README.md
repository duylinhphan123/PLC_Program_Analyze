# PLC S7-400H PALLETIZING SYSTEM ANALYSIS PROJECT
===============================================

## Tổng quan dự án
Dự án phân tích và phát triển hệ thống PLC S7-400H điều khiển palletizing kết nối với robot ABB IRC5. Bao gồm các giải pháp trao đổi dữ liệu, mô phỏng và tối ưu hóa hệ thống.

**Ngày tạo:** 17/07/2025  
**Hệ thống:** Siemens S7-400H CPU 412-3H + ABB Robot IRC5  
**Ứng dụng:** Palletizing automation với 2 khu vực sản xuất độc lập  

---

## Cấu trúc dự án

### 📁 Thư mục chính
```
PLC_Program_Analyze/
├── STL_Program.txt                    # Chương trình STL gốc (26,495 dòng)
├── main_signal_flow.txt               # Kiến trúc tổng thể hệ thống
├── main_signal_flow_detail.txt        # Sơ đồ luồng chi tiết
├── coordinate_exchange_solution.txt   # Giải pháp trao đổi tọa độ
├── simulation_solution.txt            # Giải pháp mô phỏng Robot Studio
├── plc_io.txt                        # Mapping chi tiết I/O PLC (Digital Inputs/Outputs)
├── DB100.asc                         # Data Block 100 export file
├── backup/                           # Thư mục backup tự động
├── guide/                            # Hướng dẫn cấu hình và AWL files
├── source_plc_simulation/            # Source code AWL cho simulation
└── README.md                         # Tài liệu này
```

### 📁 Thư mục backup
Tự động backup tất cả file .txt với timestamp theo format: `filename_backup_YYYYMMDD_HHMMSS.txt`

### 📁 Thư mục guide
Chứa các hướng dẫn chi tiết và file AWL:
```
guide/
├── data_block_properties.txt          # Hướng dẫn cấu hình Data Block
├── DB100_CoordinateExchange.awl       # DB100 AWL definition
├── DB101_RobotBuffer.awl              # DB101 AWL definition  
├── DB102_SystemDiagnostics.awl        # DB102 AWL definition
├── DB100_Table.txt                    # DB100 structure table
├── DB101_Table.txt                    # DB101 structure table
├── DB102_Table.txt                    # DB102 structure table
├── DB_Tables_Structure.txt            # Tổng quan cấu trúc DB
└── All_DataBlocks.awl                 # Tất cả DB definitions
```

### 📁 Thư mục source_plc_simulation
Chứa source code AWL hoàn chỉnh cho simulation:
```
source_plc_simulation/
├── OB1_Main.awl                       # Organization Block 1 - Main program
├── OB35_CyclicInterrupt.awl           # Organization Block 35 - 100ms interrupt
├── FB5_SafetyLogic.awl                # Function Block 5 - Safety logic
├── FC50_Area1Control.awl              # Function 50 - Area 1 control logic
├── FC52_Area1RobotComm.awl            # Function 52 - Area 1 robot communication
├── FC200_LaptopComm.awl               # Function 200 - Laptop communication
├── FC201_WriteCoordinate.awl          # Function 201 - Write coordinate set
└── Complete_System_Overview.awl       # Complete system overview and documentation
```

---

## Phân tích hệ thống

### 🔍 Phân tích chương trình STL
**Kết quả phân tích:**
- **Hệ thống:** S7-400H với CPU 412-3H (High Availability)
- **Kiến trúc:** Redundant system với failover time <100ms
- **Ứng dụng:** Palletizing system với 2 khu vực độc lập
- **Quy mô:** 26,495 dòng code STL
- **Cấu trúc chính:**
  - Data Blocks: DB1-DB7 (Area 1), DB55-DB60 (Area 2)
  - Function Blocks: FB5, FB7
  - Functions: FC8, FC34, FC50-FC55 (Area 1), FC60-FC65 (Area 2)
  - Organization Blocks: OB1 (Main), OB35 (100ms interrupt)

### 📊 Kiến trúc tổng thể hệ thống
**File:** `main_signal_flow.txt`

**Kiến trúc chính:**
```
┌─────────────────────────────────────────┐
│          SIEMENS S7-400H PLC           │
│        (High Availability System)       │
├────────────────┬────────────────────────┤
│    AREA 1      │         AREA 2         │
│   (LINE 1)     │        (LINE 2)        │
├────────────────┴────────────────────────┤
│  CPU 412-3H    │    CPU 412-3H         │
│  (Primary)     │    (Secondary)         │
└─────────────────────────────────────────┘
         │                    │
    ┌────▼────┐        ┌─────▼────┐
    │ ROBOT   │        │ ROBOT    │
    │ ABB IRC5│        │ ABB IRC5 │
    │ AREA 1  │        │ AREA 2   │
    └─────────┘        └──────────┘
```

### 🔬 Sơ đồ luồng chi tiết
**File:** `main_signal_flow_detail.txt`

**Luồng xử lý chi tiết:**
1. **Input Processing:** I0.x - I5.x signals
2. **Main Control Logic:** FC50/FC60 (Area 1/2)
3. **Robot Communication:** FC52/FC62
4. **Position Control:** FC53/FC63
5. **Safety Interlocks:** FC54/FC64
6. **Data Logging:** FC55/FC65

### 🔌 Cấu hình I/O PLC
**File:** `plc_io.txt`

**Digital Inputs (24 channels):**
- **I0.0-I0.7:** Controls & Safety (Start/Stop, Emergency Stop, Reset, Pallet Up/Down)
- **I1.0-I1.7:** Safety Systems (Safety Doors, Pallet Locating, Safety Photocells)
- **I4.0-I4.7:** Conveyor Sensors (Roller, Flattening, Pool, Patterning 1&2, Pallet positions)
- **I5.0-I5.7:** System Status (Loaded-pallet positions, Pallet Table positions, Air pressure)

**Digital Outputs (24 channels):**
- **Q32.0-Q32.7:** Alarms & Status (Sound/Light alarm, Network control, Status indicators)
- **Q33.0-Q33.7:** Conveyor Motors (Roller, Patterning 1&2, Heating/Dehumidification)
- **Q36.0-Q36.7:** Conveyor Control (Flattener, Pool, Pallet, Loaded-pallet 1-3)
- **Q37.0-Q37.7:** Pneumatic Control (Pallet Table, Fork, Locating Device, Manipulators)

**Hardware Modules:**
- **-PLC1/-PLC4:** DI modules 6ES7 321-7BH01-0ABO
- **-PLC2/-PLC5:** DI modules 6ES7 321-7BH01-0ABO  
- **-PLC11/-PLC14:** DO modules 6ES7 322-8BH01-0ABO
- **-PLC12/-PLC15:** DO modules 6ES7 322-8BH01-0ABO

### 🔄 Giải pháp trao đổi tọa độ
**File:** `coordinate_exchange_solution.txt`

**Kiến trúc trao đổi:**
```
┌─────────────┐    Ethernet/TCP    ┌─────────────┐    PROFIBUS-DP    ┌─────────────┐
│   LAPTOP    │◄─────────────────►│   PLC S7    │◄────────────────►│ ROBOT ABB   │
│  (Client)   │     S7 Protocol    │   400H      │   Digital I/O     │    IRC5     │
│             │     Port 102       │ CPU 412-3H  │   + Data Words    │             │
└─────────────┘                    └─────────────┘                   └─────────────┘
```

**Tính năng chính:**
- **DB100:** Laptop Communication Interface
- **DB101:** Robot Communication Buffer  
- **DB102:** System Status & Diagnostics
- **Functions:** FC200-FC205 cho xử lý tọa độ
- **Protocol:** Handshake với error handling
- **Real-time:** Monitoring và data validation

### � Giải pháp mô phỏng Robot Studio
**File:** `simulation_solution.txt`

**Kiến trúc mô phỏng:**
```
┌─────────────────┐    TCP/IP     ┌─────────────────┐    Virtual I/O    ┌─────────────────┐
│   ABB ROBOT     │◄─────────────►│   PC GATEWAY    │◄─────────────────►│   SIMATIC       │
│    STUDIO       │   Port 1025   │   (Middleware)  │    S7-PLCSIM      │   S7-PLCSIM     │
│   (Virtual)     │   Real Time   │   Data Broker   │    Advanced       │   (Virtual)     │
└─────────────────┘               └─────────────────┘                   └─────────────────┘
```

**Đặc điểm:**
- **Virtual Environment:** Loại bỏ hoàn toàn tầng vật lý
- **RAPID Programming:** Simulation logic cho robot
- **Python Middleware:** Gateway trao đổi dữ liệu
- **Real-time Testing:** Kiểm tra chức năng không cần hardware

### 📋 Xây dựng Document
**File:** `README.md` (file hiện tại)

**Nội dung:**
- Tổng quan dự án và cấu trúc
- Phân tích hệ thống
- Hướng dẫn sử dụng và triển khai
- Tài liệu tham khảo và changelog

### 🔧 Hướng dẫn Data Block
**File:** `guide/data_block_properties.txt`

**Nội dung hướng dẫn:**
- Cấu hình Data Block trong SIMATIC Manager
- Định nghĩa structure cho DB100-DB102
- Address mapping và data types
- Best practices và troubleshooting

### 💾 Tạo AWL Files
**Files:** `guide/DB100_CoordinateExchange.awl`, `guide/DB101_RobotBuffer.awl`, `guide/DB102_SystemDiagnostics.awl`

**Đặc điểm:**
- **AWL Format:** Định nghĩa Data Block theo chuẩn Siemens
- **Complete Structure:** Tất cả variables và initial values
- **Ready-to-use:** Import trực tiếp vào SIMATIC Manager
- **Documented:** Comments chi tiết cho từng field

### 🛠️ Prompt 9: Cập nhật README.md
**File:** `README.md`

**Hoạt động:**
- Review toàn bộ project files
- Cập nhật với thông tin mới nhất từ tất cả prompts
- Backup file README.md cũ
- Đồng bộ thông tin từ tất cả các file

### 💻 Viết Source Code AWL
**Thư mục:** `source_plc_simulation/`

**Nội dung:**
- **OB1_Main.awl:** Main program với cyclic execution
- **OB35_CyclicInterrupt.awl:** 100ms interrupt cho time-critical tasks
- **FB5_SafetyLogic.awl:** Safety logic function block (SIL 2)
- **FC50_Area1Control.awl:** Area 1 main control logic
- **FC52_Area1RobotComm.awl:** Robot communication protocol
- **FC200_LaptopComm.awl:** Laptop communication handler
- **FC201_WriteCoordinate.awl:** Write coordinate set function
- **Complete_System_Overview.awl:** Tổng quan hệ thống và usage instructions

### 🎮 Giải pháp mô phỏng Robot Studio
**File:** `simulation_solution.txt`

**Kiến trúc mô phỏng:**
```
┌─────────────────┐    TCP/IP     ┌─────────────────┐    Virtual I/O    ┌─────────────────┐
│   ABB ROBOT     │◄─────────────►│   PC GATEWAY    │◄─────────────────►│   SIMATIC       │
│    STUDIO       │   Port 1025   │   (Middleware)  │    S7-PLCSIM      │   S7-PLCSIM     │
│   (Virtual)     │   Real Time   │   Data Broker   │    Advanced       │   (Virtual)     │
└─────────────────┘               └─────────────────┘                   └─────────────────┘
```

**Thành phần mô phỏng:**
- **Robot Studio:** IRB 6640 virtual controller
- **S7-PLCSIM Advanced:** Virtual PLC simulation
- **Python Gateway:** Middleware cho data exchange
- **RAPID Code:** Socket communication với PLC
- **Testing Framework:** Unit và integration testing

---

## Tính năng kỹ thuật

### 🔧 Đặc điểm hệ thống
- **High Availability:** Redundant CPU với hot-standby
- **Real-time Performance:** Cycle time <100ms
- **Dual Area Control:** 2 khu vực palletizing độc lập
- **Robot Integration:** ABB IRC5 qua PROFIBUS-DP
- **Data Integrity:** Handshake protocol và error handling
- **I/O Configuration:** 
  - Digital Inputs: 24 channels (I0.0-I5.7)
  - Digital Outputs: 24 channels (Q32.0-Q37.7)
  - Safety Systems: Emergency stops, safety doors, photocells
  - Conveyor Control: 10 different conveyor systems
  - Pneumatic Control: Solenoid valves cho pallet table, fork, locating device

### 📡 Giao tiếp
- **Laptop ↔ PLC:** Ethernet TCP/IP, S7 Protocol (Port 102)
- **PLC ↔ Robot:** PROFIBUS-DP, Digital I/O + Data Words
- **Simulation:** TCP/IP Socket (Port 1025)
- **Data Format:** 16-bit words, Big-endian

### 🛡️ An toàn
- **Emergency Stop:** Integrated safety systems
- **Redundancy:** Automatic failover
- **Error Monitoring:** Real-time diagnostics
- **Data Validation:** Checksum và range checking

---

## Hướng dẫn sử dụng

### 🚀 Triển khai hệ thống thực
1. **PLC Setup:**
   - Load STL_Program.txt vào CPU 412-3H
   - Configure redundant system
   - Set up PROFIBUS-DP communication

2. **Robot Setup:**
   - Configure ABB IRC5 controller
   - Set up PROFIBUS-DP interface
   - Load robot program

3. **Coordinate Exchange:**
   - Add DB100-DB102 structures
   - Implement FC200-FC205 functions
   - Configure S7 communication

### 🧪 Môi trường mô phỏng
1. **Robot Studio:**
   - Install RobotStudio 2023.1+
   - Create IRB 6640 station
   - Configure PC Interface

2. **PLC Simulation:**
   - Install S7-PLCSIM Advanced
   - Load modified STL program
   - Enable simulation mode

3. **Gateway Setup:**
   - Install Python 3.8+
   - Install snap7 library
   - Run gateway application

---

## Kết quả đạt được

### ✅ Phân tích chương trình STL
- [x] Hiểu rõ cấu trúc chương trình STL
- [x] Xác định kiến trúc hệ thống
- [x] Mapping các function blocks

### ✅ Kiến trúc tổng thể
- [x] Sơ đồ luồng tổng thể
- [x] Cấu trúc data blocks
- [x] Organization blocks mapping

### ✅ Sơ đồ chi tiết
- [x] Luồng xử lý từng bước
- [x] Input/Output mapping
- [x] Safety interlocks

### ✅ Trao đổi tọa độ
- [x] Kiến trúc 3-tier: Laptop-PLC-Robot
- [x] Protocol handshake
- [x] Real-time data exchange
- [x] Error handling

### ✅ Mô phỏng Robot Studio
- [x] Virtual environment setup
- [x] RAPID programming
- [x] Python middleware
- [x] Testing framework

### ✅ Xây dựng Documentation
- [x] Tổng quan dự án
- [x] Cấu trúc file và thư mục
- [x] Phân tích chi tiết
- [x] Hướng dẫn sử dụng

### ✅ Hướng dẫn Data Block
- [x] Tạo file guide/data_block_properties.txt
- [x] Hướng dẫn cấu hình SIMATIC Manager
- [x] Structure definition chi tiết
- [x] Best practices và troubleshooting

### ✅ Tạo AWL Files
- [x] DB100_CoordinateExchange.awl
- [x] DB101_RobotBuffer.awl
- [x] DB102_SystemDiagnostics.awl
- [x] All_DataBlocks.awl (tổng hợp)
- [x] Table structure documentation

### ✅ Hoàn thiện Documentation
- [x] Review toàn bộ project files
- [x] Cập nhật README.md với thông tin mới nhất
- [x] Backup file README.md cũ
- [x] Đồng bộ thông tin từ tất cả các file

### ✅ Viết Source Code AWL
- [x] Đọc lại toàn bộ project và README.md
- [x] Tạo thư mục source_plc_simulation
- [x] Viết OB1_Main.awl - Main program
- [x] Viết OB35_CyclicInterrupt.awl - 100ms interrupt  
- [x] Viết FB5_SafetyLogic.awl - Safety logic
- [x] Viết FC50_Area1Control.awl - Area 1 control
- [x] Viết FC52_Area1RobotComm.awl - Robot communication
- [x] Viết FC200_LaptopComm.awl - Laptop communication
- [x] Viết FC201_WriteCoordinate.awl - Write coordinate
- [x] Tạo Complete_System_Overview.awl - System overview

### ✅ Đánh dấu thay đổi và cập nhật
- [x] Đọc lại file README.md
- [x] Xem lại tất cả các phân tích trước đó
- [x] Đánh dấu những thay đổi đáng kể
- [x] Thêm hướng dẫn sử dụng source code AWL
- [x] Cập nhật documentation với testing guidelines
- [x] Hoàn thiện troubleshooting guide

---

## 🚀 Hướng dẫn sử dụng Source Code AWL

### 📋 Yêu cầu hệ thống
**Phần mềm cần thiết:**
- SIMATIC Manager (STEP 7 v5.x)
- S7-PLCSIM Advanced (cho simulation)
- TIA Portal (tùy chọn, cho migration)
- Hardware: S7-400H CPU 412-3H hoặc simulator

**Cấu hình tối thiểu:**
- RAM: 8GB
- Storage: 2GB free space
- Network: Ethernet cho communication testing
- OS: Windows 10/11 Professional

### 🛠️ Cách import AWL files vào SIMATIC Manager

#### Bước 1: Tạo project mới
```
1. Mở SIMATIC Manager
2. File → New → Project
3. Tên project: "PLC_Palletizing_Simulation"
4. Chọn CPU: S7-400H → CPU 412-3H
5. Configure hardware modules
```

#### Bước 2: Import Organization Blocks
```
1. Right-click "Blocks" folder
2. Insert → External Source → Import
3. Chọn file: source_plc_simulation/OB1_Main.awl
4. Compile và check syntax
5. Lặp lại cho OB35_CyclicInterrupt.awl
```

#### Bước 3: Import Function Blocks
```
1. Import FB5_SafetyLogic.awl
2. Configure FB5 instance data blocks
3. Verify safety logic parameters
```

#### Bước 4: Import Functions
```
1. Import FC50_Area1Control.awl
2. Import FC52_Area1RobotComm.awl
3. Import FC200_LaptopComm.awl
4. Import FC201_WriteCoordinate.awl
5. Configure function parameters
```

#### Bước 5: Import Data Blocks
```
1. Import từ guide/:
   - DB100_CoordinateExchange.awl
   - DB101_RobotBuffer.awl
   - DB102_SystemDiagnostics.awl
2. Verify data structure
3. Set initial values
```

### ⚙️ Cấu hình Hardware

#### CPU Configuration
```
Slot 2: CPU 412-3H
- Memory: 8MB RAM
- Cycle time: 100ms
- Priority: OB1=1, OB35=10
- Interrupt: Enable OB35 (100ms)
```

#### I/O Configuration
```
Digital Inputs (24 channels):
I0.0: -SBH3 Fault Reset
I0.1: -KA1 Emergency Stop Signal  
I0.2: -QF20 Motor Circuit Breaker
I0.4: -SBH1 Start Button
I0.5: -SBH2 Stop Button
I0.6: -SB4 Pallet Up Button
I0.7: -SB5 Pallet Down Button

I1.0: -SQ01 Safety Door 1 Closed
I1.1: -SQ02 Safety Door 2 Closed
I1.4: -SQ4 Pallet Locating Device Lower pos.
I1.7: -SG16A/B/AE/BE Safety Photocell

I4.0: -SG1 Roller Conveyor pos.
I4.1: -SG2 Flattening Conveyor pos.
I4.2: -SG3 Pool Conveyor pos.
I4.3: -SG4 Patterning Conveyor 2 pos.
I4.4: -SG5 Patterning Conveyor 1 pos.
I4.5: -SG6 Pallet Insufficient
I4.6: -SG7 Pallet Conveying pos.
I4.7: -SG8 Pallet Waiting pos.

I5.0: -SG9 Loaded-pallet Conveyor Inlet
I5.1: -SQ1 Pallet Table Upper pos.
I5.2: -SQ2 Pallet Table Middle pos.
I5.3: -SQ3 Loaded-pallet Conveyor 1 pos.
I5.4: -SQ5 Loaded-pallet Conveyor 2 pos.
I5.5: -SQ6 Loaded-pallet Conveyor 3 pos.
I5.6: -SQ7 Loaded-pallet Conveyor 4 pos.
I5.7: -SP1 Air-pressure detecting switch

Digital Outputs (24 channels):
Q32.0: -KA2 Sound and Light Alarm
Q32.1: Network Segment SEL 1
Q32.2: Network Segment SEL 2
Q32.3: -KAS Running Indicator Light
Q32.4: -KA6 Stopping Status Signal
Q32.5: -KA3 Fault Indicator Light
Q32.6: System Stand by Signal

Q33.0: -KM20 Heating & Dehumidification
Q33.1: -KM1 Roller Conveyor
Q33.2: -KM5 Patterning Conveyor 2
Q33.3: -KM6 Patterning Conveyor 1

Q36.0: -KM2 Flattener
Q36.1: -KM3 Flattening Conveyor
Q36.2: -KM4 Pool Conveyor
Q36.4: -KM7 Pallet Conveyor
Q36.5: -KM8 Loaded-pallet Conveyor 1
Q36.6: -KM9 Loaded-pallet Conveyor 2
Q36.7: -KM10 Loaded-pallet Conveyor 3

Q37.0: -YV1 Pallet Table Solenoid Valve
Q37.1: -YV2 Pallet Fork Solenoid Valve
Q37.2: -YV3 Pallet Locating Device Solenoid Valve
Q37.3: Manipulator 1 Control Signal
Q37.4: Manipulator 2 Control Signal
```

### 🔧 Cấu hình Simulation

#### S7-PLCSIM Setup
```
1. Mở S7-PLCSIM Advanced
2. Create new simulation:
   - Name: "Palletizing_Simulation"
   - CPU: S7-400H
   - IP: 192.168.1.100
3. Load compiled project
4. Start simulation
```

#### Virtual I/O Configuration
```
1. Configure virtual inputs:
   - I0.0, I0.4 = TRUE (Emergency stops OK)
   - I65.5 = TRUE (Light curtain OK)
   - I4.0, I4.1, I4.2 = TRUE (Robot ready)

2. Monitor virtual outputs:
   - Q32.0: Conveyor motor
   - Q36.0: Robot enable
   - Q65.0-Q65.7: Status lamps
```

### 📊 Testing và Validation

#### Test Sequence 1: Basic System
```
1. Start simulation
2. Monitor M1.1 (Safety OK)
3. Check M12.0 (Area 1 enable)
4. Verify Q65.0 (Running lamp)
5. Test emergency stop sequence
```

#### Test Sequence 2: Communication
```
1. Write to DB100.DBW0 = 1 (Write command)
2. Set coordinate data in DB100
3. Monitor DB100.DBW2 (Status response)
4. Verify DB102 storage
5. Test error handling
```

#### Test Sequence 3: Robot Interface
```
1. Enable robot communication
2. Monitor I64.0 (Robot handshake)
3. Check Q64.0 (PLC handshake)
4. Test position commands
5. Verify feedback data
```

### 🐛 Troubleshooting

#### Common Issues
```
Compile Errors:
- Check AWL syntax
- Verify DB structure
- Confirm I/O addresses

Runtime Errors:
- Check safety conditions
- Verify communication timeouts
- Monitor error codes in DB102

Communication Issues:
- Check IP configuration
- Verify S7 protocol settings
- Test handshake sequences
```

#### Error Codes Reference
```
0001-0010: Input validation errors
0011-0020: Safety system errors
0021-0030: Communication errors
0031-0040: Robot interface errors
0041-0050: Coordinate system errors
8000-8999: PLC internal errors
```

### 📈 Performance Monitoring

#### Key Monitoring Points
```
- MW510: Area 1 status word
- MW520: Area 2 status word
- MD500: Cycle counter
- MW550: Execution time
- DB100.DBW2: Communication status
```

#### Performance Targets
```
- Cycle time: <10ms average
- Communication response: <100ms
- Safety reaction: <50ms
- Robot handshake: <200ms
```

### 🔄 Maintenance và Updates

#### Regular Maintenance
```
1. Backup project weekly
2. Check error logs daily
3. Update counters monthly
4. Test safety systems quarterly
```

#### Version Control
```
1. Use Git for source control
2. Tag releases with version numbers
3. Document all changes
4. Maintain changelog
```

---

## Tài liệu tham khảo

### 📚 Tài liệu kỹ thuật
- **Siemens S7-400H:** Programming Manual
- **ABB IRC5:** RAPID Programming Guide
- **PROFIBUS-DP:** Communication Protocol
- **Robot Studio:** User Manual

### 🔗 File liên quan
- `STL_Program.txt` - Chương trình gốc (26,495 dòng)
- `main_signal_flow.txt` - Kiến trúc hệ thống tổng thể
- `main_signal_flow_detail.txt` - Sơ đồ luồng chi tiết
- `coordinate_exchange_solution.txt` - Giải pháp trao đổi tọa độ
- `simulation_solution.txt` - Giải pháp mô phỏng Robot Studio
- `plc_io.txt` - Mapping chi tiết I/O PLC (Digital Inputs/Outputs)
- `DB100.asc` - Data Block 100 export file
- `guide/data_block_properties.txt` - Hướng dẫn cấu hình Data Block
- `guide/DB100_CoordinateExchange.awl` - AWL definition cho DB100
- `guide/DB101_RobotBuffer.awl` - AWL definition cho DB101
- `guide/DB102_SystemDiagnostics.awl` - AWL definition cho DB102
- `guide/All_DataBlocks.awl` - Tổng hợp tất cả DB definitions
- `source_plc_simulation/OB1_Main.awl` - Main program AWL
- `source_plc_simulation/OB35_CyclicInterrupt.awl` - Cyclic interrupt AWL
- `source_plc_simulation/FB5_SafetyLogic.awl` - Safety logic AWL
- `source_plc_simulation/FC50_Area1Control.awl` - Area 1 control AWL
- `source_plc_simulation/FC52_Area1RobotComm.awl` - Robot communication AWL
- `source_plc_simulation/FC200_LaptopComm.awl` - Laptop communication AWL
- `source_plc_simulation/FC201_WriteCoordinate.awl` - Write coordinate AWL
- `source_plc_simulation/Complete_System_Overview.awl` - System overview

### 📋 Backup files
Tất cả files được backup tự động trong thư mục `backup/` với timestamp.

---

## Liên hệ & Hỗ trợ

### 🛠️ Maintenance
- **Backup:** Tự động backup files với timestamp
- **Version Control:** Theo dõi changes qua Git
- **Documentation:** Cập nhật README.md thường xuyên

### 📞 Support
- **Technical Issues:** Check troubleshooting guides
- **Development:** Follow coding standards
- **Testing:** Use provided test frameworks

---

## Changelog

### v1.1 (17/07/2025)
- ✅ Thêm file `plc_io.txt` với mapping chi tiết I/O PLC
- ✅ Cập nhật README.md với thông tin I/O configuration
- ✅ Bổ sung 24 digital inputs và 24 digital outputs
- ✅ Thêm thông tin hardware modules (6ES7 321/322)
- ✅ Cập nhật hướng dẫn với I/O addresses chính xác
- ✅ Hoàn thiện documentation với safety systems

### v1.0 (17/07/2025)
- ✅ Hoàn thành phân tích STL program (26,495 dòng)
- ✅ Tạo kiến trúc tổng thể và chi tiết
- ✅ Phát triển giải pháp trao đổi tọa độ với DB100-DB102
- ✅ Tạo giải pháp mô phỏng Robot Studio
- ✅ Hoàn thành hướng dẫn cấu hình Data Block
- ✅ Tạo tất cả AWL files cho DB100, DB101, DB102
- ✅ Viết đầy đủ source code AWL cho simulation
- ✅ Tạo 8 file AWL program blocks hoàn chỉnh
- ✅ Thêm hướng dẫn sử dụng source code AWL chi tiết
- ✅ Cập nhật testing guidelines và troubleshooting
- ✅ Hoàn thiện documentation với performance monitoring
- ✅ Cập nhật đầy đủ documentation và README.md

---

*Tài liệu này được cập nhật từ việc phân tích và thực hiện các yêu cầu phát triển trong project*

**Ngày cập nhật:** 17/07/2025  
**Trạng thái:** Hoàn thành với source code AWL và hướng dẫn chi tiết  
**© 2025 PLC S7-400H Palletizing System Analysis Project**
