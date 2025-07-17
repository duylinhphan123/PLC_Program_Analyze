MODULE Coordinate_Handler
    !***************************************************************************
    ! Coordinate Handler Module
    !***************************************************************************
    ! Description: RAPID module for coordinate management and validation
    ! Purpose: Handle coordinate operations and safety checks
    ! Version: 1.0
    ! Date: 17/07/2025
    !
    ! This module provides coordinate handling functionality including
    ! validation, transformation, and safety checks for robot operations
    !***************************************************************************
    
    ! Constants
    CONST num MAX_COORDINATE_SETS := 10;
    CONST num MAX_AREAS := 2;
    CONST num SAFETY_MARGIN := 50;      ! Safety margin in mm
    CONST num MAX_REACH := 1800;        ! Maximum robot reach in mm
    CONST num MIN_Z_HEIGHT := 10;       ! Minimum Z height for safety
    
    ! Work area definitions
    RECORD work_area
        string name;
        num x_min;
        num x_max;
        num y_min;
        num y_max;
        num z_min;
        num z_max;
        bool active;
    ENDRECORD
    
    ! Coordinate set definition
    RECORD coordinate_set
        num area;
        num set_number;
        robtarget coordinates{10};  ! Up to 10 coordinates per set
        num coordinate_count;
        string description;
        bool valid;
        num created_time;
        num last_executed_time;
    ENDRECORD
    
    ! Global variables
    VAR work_area work_areas{MAX_AREAS};
    VAR coordinate_set coordinate_sets{MAX_AREAS, MAX_COORDINATE_SETS};
    VAR robtarget home_positions{MAX_AREAS};
    VAR bool coordinate_handler_initialized := FALSE;
    VAR num validation_errors := 0;
    VAR num last_validation_time := 0;
    
    ! Safety zone definitions
    RECORD safety_zone
        string name;
        num x_min;
        num x_max;
        num y_min;
        num y_max;
        num z_min;
        num z_max;
        bool active;
        string description;
    ENDRECORD
    
    VAR safety_zone safety_zones{5};  ! Maximum 5 safety zones
    VAR num safety_zone_count := 0;
    
    !***************************************************************************
    ! PROC Initialize_Coordinate_Handler
    ! Initialize coordinate handler system
    !***************************************************************************
    PROC Initialize_Coordinate_Handler()
        ! Initialize work areas
        Initialize_Work_Areas;
        
        ! Initialize coordinate sets
        Initialize_Coordinate_Sets;
        
        ! Initialize home positions
        Initialize_Home_Positions;
        
        ! Initialize safety zones
        Initialize_Safety_Zones;
        
        ! Set initialization flag
        coordinate_handler_initialized := TRUE;
        
        TPWrite "Coordinate Handler initialized";
    ENDPROC
    
    !***************************************************************************
    ! PROC Initialize_Work_Areas
    ! Initialize work area definitions
    !***************************************************************************
    PROC Initialize_Work_Areas()
        ! Area 1 - Palletizing Area 1
        work_areas{1}.name := "Palletizing Area 1";
        work_areas{1}.x_min := -1500;
        work_areas{1}.x_max := 1500;
        work_areas{1}.y_min := -1500;
        work_areas{1}.y_max := 1500;
        work_areas{1}.z_min := 100;
        work_areas{1}.z_max := 800;
        work_areas{1}.active := TRUE;
        
        ! Area 2 - Palletizing Area 2
        work_areas{2}.name := "Palletizing Area 2";
        work_areas{2}.x_min := -1500;
        work_areas{2}.x_max := 1500;
        work_areas{2}.y_min := -1500;
        work_areas{2}.y_max := 1500;
        work_areas{2}.z_min := 100;
        work_areas{2}.z_max := 800;
        work_areas{2}.active := TRUE;
        
        TPWrite "Work areas initialized";
    ENDPROC
    
    !***************************************************************************
    ! PROC Initialize_Coordinate_Sets
    ! Initialize coordinate set storage
    !***************************************************************************
    PROC Initialize_Coordinate_Sets()
        VAR num area;
        VAR num set;
        VAR num coord;
        
        FOR area FROM 1 TO MAX_AREAS DO
            FOR set FROM 1 TO MAX_COORDINATE_SETS DO
                coordinate_sets{area, set}.area := area;
                coordinate_sets{area, set}.set_number := set;
                coordinate_sets{area, set}.coordinate_count := 0;
                coordinate_sets{area, set}.description := "";
                coordinate_sets{area, set}.valid := FALSE;
                coordinate_sets{area, set}.created_time := 0;
                coordinate_sets{area, set}.last_executed_time := 0;
                
                ! Initialize coordinates to safe default
                FOR coord FROM 1 TO 10 DO
                    coordinate_sets{area, set}.coordinates{coord} := [[0, 0, 300], [1, 0, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
                ENDFOR
            ENDFOR
        ENDFOR
        
        TPWrite "Coordinate sets initialized";
    ENDPROC
    
    !***************************************************************************
    ! PROC Initialize_Home_Positions
    ! Initialize home positions for each area
    !***************************************************************************
    PROC Initialize_Home_Positions()
        ! Home position for Area 1
        home_positions{1} := [[0, -1000, 500], [1, 0, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
        
        ! Home position for Area 2
        home_positions{2} := [[0, 1000, 500], [1, 0, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
        
        TPWrite "Home positions initialized";
    ENDPROC
    
    !***************************************************************************
    ! PROC Initialize_Safety_Zones
    ! Initialize safety zones
    !***************************************************************************
    PROC Initialize_Safety_Zones()
        ! Safety zone 1 - Conveyor area
        safety_zones{1}.name := "Conveyor Zone";
        safety_zones{1}.x_min := -200;
        safety_zones{1}.x_max := 200;
        safety_zones{1}.y_min := -100;
        safety_zones{1}.y_max := 100;
        safety_zones{1}.z_min := 0;
        safety_zones{1}.z_max := 200;
        safety_zones{1}.active := TRUE;
        safety_zones{1}.description := "Conveyor belt area - avoid collision";
        
        ! Safety zone 2 - Fixture area
        safety_zones{2}.name := "Fixture Zone";
        safety_zones{2}.x_min := -100;
        safety_zones{2}.x_max := 100;
        safety_zones{2}.y_min := -50;
        safety_zones{2}.y_max := 50;
        safety_zones{2}.z_min := 0;
        safety_zones{2}.z_max := 150;
        safety_zones{2}.active := TRUE;
        safety_zones{2}.description := "Fixture area - restricted access";
        
        safety_zone_count := 2;
        
        TPWrite "Safety zones initialized";
    ENDPROC
    
    !***************************************************************************
    ! FUNC Validate_Coordinate_Set
    ! Validate complete coordinate set
    !***************************************************************************
    FUNC bool Validate_Coordinate_Set(num area, num set_number)
        VAR bool result := TRUE;
        VAR num coord;
        
        ! Check if handler is initialized
        IF coordinate_handler_initialized = FALSE THEN
            TPWrite "Coordinate handler not initialized";
            RETURN FALSE;
        ENDIF
        
        ! Validate area
        IF area < 1 OR area > MAX_AREAS THEN
            TPWrite "Invalid area: " + NumToStr(area, 0);
            RETURN FALSE;
        ENDIF
        
        ! Validate set number
        IF set_number < 1 OR set_number > MAX_COORDINATE_SETS THEN
            TPWrite "Invalid set number: " + NumToStr(set_number, 0);
            RETURN FALSE;
        ENDIF
        
        ! Check if work area is active
        IF work_areas{area}.active = FALSE THEN
            TPWrite "Work area " + NumToStr(area, 0) + " is not active";
            RETURN FALSE;
        ENDIF
        
        ! Validate each coordinate in the set
        FOR coord FROM 1 TO coordinate_sets{area, set_number}.coordinate_count DO
            IF Validate_Single_Coordinate(coordinate_sets{area, set_number}.coordinates{coord}, area) = FALSE THEN
                TPWrite "Coordinate " + NumToStr(coord, 0) + " in set " + NumToStr(set_number, 0) + " failed validation";
                result := FALSE;
            ENDIF
        ENDFOR
        
        ! Update validation status
        coordinate_sets{area, set_number}.valid := result;
        last_validation_time := GetTime();
        
        IF result = FALSE THEN
            validation_errors := validation_errors + 1;
        ENDIF
        
        RETURN result;
    ENDFUNC
    
    !***************************************************************************
    ! FUNC Validate_Single_Coordinate
    ! Validate single coordinate
    !***************************************************************************
    FUNC bool Validate_Single_Coordinate(robtarget target, num area)
        VAR bool result := TRUE;
        VAR num distance;
        
        ! Check workspace limits
        IF target.trans.x < work_areas{area}.x_min OR target.trans.x > work_areas{area}.x_max THEN
            TPWrite "X coordinate out of range: " + NumToStr(target.trans.x, 1);
            result := FALSE;
        ENDIF
        
        IF target.trans.y < work_areas{area}.y_min OR target.trans.y > work_areas{area}.y_max THEN
            TPWrite "Y coordinate out of range: " + NumToStr(target.trans.y, 1);
            result := FALSE;
        ENDIF
        
        IF target.trans.z < work_areas{area}.z_min OR target.trans.z > work_areas{area}.z_max THEN
            TPWrite "Z coordinate out of range: " + NumToStr(target.trans.z, 1);
            result := FALSE;
        ENDIF
        
        ! Check minimum Z height for safety
        IF target.trans.z < MIN_Z_HEIGHT THEN
            TPWrite "Z coordinate below minimum safe height: " + NumToStr(target.trans.z, 1);
            result := FALSE;
        ENDIF
        
        ! Check maximum reach
        distance := Sqrt(target.trans.x * target.trans.x + target.trans.y * target.trans.y + target.trans.z * target.trans.z);
        IF distance > MAX_REACH THEN
            TPWrite "Target out of reach: " + NumToStr(distance, 1) + " mm";
            result := FALSE;
        ENDIF
        
        ! Check safety zones
        IF Check_Safety_Zones(target) = FALSE THEN
            TPWrite "Target in safety zone";
            result := FALSE;
        ENDIF
        
        ! Check reachability (simplified)
        IF Check_Reachability(target) = FALSE THEN
            TPWrite "Target not reachable";
            result := FALSE;
        ENDIF
        
        RETURN result;
    ENDFUNC
    
    !***************************************************************************
    ! FUNC Check_Safety_Zones
    ! Check if coordinate is in safety zone
    !***************************************************************************
    FUNC bool Check_Safety_Zones(robtarget target)
        VAR num i;
        
        FOR i FROM 1 TO safety_zone_count DO
            IF safety_zones{i}.active = TRUE THEN
                IF target.trans.x >= safety_zones{i}.x_min AND target.trans.x <= safety_zones{i}.x_max AND
                   target.trans.y >= safety_zones{i}.y_min AND target.trans.y <= safety_zones{i}.y_max AND
                   target.trans.z >= safety_zones{i}.z_min AND target.trans.z <= safety_zones{i}.z_max THEN
                    TPWrite "Target in safety zone: " + safety_zones{i}.name;
                    RETURN FALSE;
                ENDIF
            ENDIF
        ENDFOR
        
        RETURN TRUE;
    ENDFUNC
    
    !***************************************************************************
    ! FUNC Check_Reachability
    ! Check if coordinate is reachable by robot
    !***************************************************************************
    FUNC bool Check_Reachability(robtarget target)
        VAR bool result := TRUE;
        
        ! This is a simplified reachability check
        ! In a real implementation, you would use more sophisticated algorithms
        ! or built-in robot functions if available
        
        ! Check if target is within robot's workspace envelope
        VAR num reach_distance;
        reach_distance := Sqrt(target.trans.x * target.trans.x + target.trans.y * target.trans.y);
        
        ! Check horizontal reach
        IF reach_distance > 1700 THEN  ! Approximate horizontal reach limit
            result := FALSE;
        ENDIF
        
        ! Check vertical limits
        IF target.trans.z > 1000 THEN  ! Approximate vertical reach limit
            result := FALSE;
        ENDIF
        
        ! Check for singularities (simplified)
        IF reach_distance < 100 THEN  ! Too close to robot base
            result := FALSE;
        ENDIF
        
        RETURN result;
    ENDFUNC
    
    !***************************************************************************
    ! PROC Store_Coordinate
    ! Store coordinate in coordinate set
    !***************************************************************************
    PROC Store_Coordinate(num area, num set_number, robtarget target, string description)
        ! Validate inputs
        IF area < 1 OR area > MAX_AREAS THEN
            TPWrite "Invalid area: " + NumToStr(area, 0);
            RETURN;
        ENDIF
        
        IF set_number < 1 OR set_number > MAX_COORDINATE_SETS THEN
            TPWrite "Invalid set number: " + NumToStr(set_number, 0);
            RETURN;
        ENDIF
        
        ! Validate coordinate before storing
        IF Validate_Single_Coordinate(target, area) = FALSE THEN
            TPWrite "Coordinate validation failed - not stored";
            RETURN;
        ENDIF
        
        ! Store coordinate
        coordinate_sets{area, set_number}.coordinates{1} := target;
        coordinate_sets{area, set_number}.coordinate_count := 1;
        coordinate_sets{area, set_number}.description := description;
        coordinate_sets{area, set_number}.valid := TRUE;
        coordinate_sets{area, set_number}.created_time := GetTime();
        
        TPWrite "Coordinate stored in set [" + NumToStr(area, 0) + "," + NumToStr(set_number, 0) + "]";
    ENDPROC
    
    !***************************************************************************
    ! FUNC Get_Coordinate
    ! Get coordinate from coordinate set
    !***************************************************************************
    FUNC robtarget Get_Coordinate(num area, num set_number, num coordinate_index)
        VAR robtarget result;
        
        ! Validate inputs
        IF area < 1 OR area > MAX_AREAS THEN
            TPWrite "Invalid area: " + NumToStr(area, 0);
            result := [[0, 0, 300], [1, 0, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
            RETURN result;
        ENDIF
        
        IF set_number < 1 OR set_number > MAX_COORDINATE_SETS THEN
            TPWrite "Invalid set number: " + NumToStr(set_number, 0);
            result := [[0, 0, 300], [1, 0, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
            RETURN result;
        ENDIF
        
        IF coordinate_index < 1 OR coordinate_index > coordinate_sets{area, set_number}.coordinate_count THEN
            TPWrite "Invalid coordinate index: " + NumToStr(coordinate_index, 0);
            result := [[0, 0, 300], [1, 0, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
            RETURN result;
        ENDIF
        
        ! Check if coordinate set is valid
        IF coordinate_sets{area, set_number}.valid = FALSE THEN
            TPWrite "Coordinate set not valid";
            result := [[0, 0, 300], [1, 0, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
            RETURN result;
        ENDIF
        
        result := coordinate_sets{area, set_number}.coordinates{coordinate_index};
        RETURN result;
    ENDFUNC
    
    !***************************************************************************
    ! PROC Move_To_Home
    ! Move robot to home position for specified area
    !***************************************************************************
    PROC Move_To_Home(num area, speeddata speed, zonedata zone)
        ! Validate area
        IF area < 1 OR area > MAX_AREAS THEN
            TPWrite "Invalid area: " + NumToStr(area, 0);
            RETURN;
        ENDIF
        
        ! Check if work area is active
        IF work_areas{area}.active = FALSE THEN
            TPWrite "Work area " + NumToStr(area, 0) + " is not active";
            RETURN;
        ENDIF
        
        ! Move to home position
        TPWrite "Moving to home position for area " + NumToStr(area, 0);
        MoveJ home_positions{area}, speed, zone, Tool0 \WObj:=WObj0;
        
        TPWrite "Reached home position for area " + NumToStr(area, 0);
    ENDPROC
    
    !***************************************************************************
    ! PROC Execute_Coordinate_Sequence
    ! Execute sequence of coordinates
    !***************************************************************************
    PROC Execute_Coordinate_Sequence(num area, num set_number, speeddata speed, zonedata zone)
        VAR num coord;
        VAR robtarget target;
        
        ! Validate coordinate set
        IF Validate_Coordinate_Set(area, set_number) = FALSE THEN
            TPWrite "Coordinate set validation failed";
            RETURN;
        ENDIF
        
        ! Move to home position first
        Move_To_Home(area, speed, zone);
        
        ! Execute each coordinate in sequence
        FOR coord FROM 1 TO coordinate_sets{area, set_number}.coordinate_count DO
            target := coordinate_sets{area, set_number}.coordinates{coord};
            
            TPWrite "Executing coordinate " + NumToStr(coord, 0) + " of " + NumToStr(coordinate_sets{area, set_number}.coordinate_count, 0);
            
            ! Execute motion
            MoveL target, speed, zone, Tool0 \WObj:=WObj0;
            
            ! Small delay between movements
            WaitTime 0.1;
        ENDFOR
        
        ! Update last executed time
        coordinate_sets{area, set_number}.last_executed_time := GetTime();
        
        ! Return to home position
        Move_To_Home(area, speed, zone);
        
        TPWrite "Coordinate sequence completed";
    ENDPROC
    
    !***************************************************************************
    ! FUNC Transform_Coordinate
    ! Transform coordinate from one coordinate system to another
    !***************************************************************************
    FUNC robtarget Transform_Coordinate(robtarget input_target, pose transformation)
        VAR robtarget result;
        
        ! Apply transformation (simplified - would use proper transformation functions)
        result := input_target;
        
        ! Translate
        result.trans.x := result.trans.x + transformation.trans.x;
        result.trans.y := result.trans.y + transformation.trans.y;
        result.trans.z := result.trans.z + transformation.trans.z;
        
        ! Rotate (simplified - proper implementation would use quaternion math)
        result.rot := result.rot * transformation.rot;
        
        RETURN result;
    ENDFUNC
    
    !***************************************************************************
    ! PROC Clear_Coordinate_Set
    ! Clear coordinate set
    !***************************************************************************
    PROC Clear_Coordinate_Set(num area, num set_number)
        VAR num coord;
        
        ! Validate inputs
        IF area < 1 OR area > MAX_AREAS THEN
            TPWrite "Invalid area: " + NumToStr(area, 0);
            RETURN;
        ENDIF
        
        IF set_number < 1 OR set_number > MAX_COORDINATE_SETS THEN
            TPWrite "Invalid set number: " + NumToStr(set_number, 0);
            RETURN;
        ENDIF
        
        ! Clear coordinate set
        coordinate_sets{area, set_number}.coordinate_count := 0;
        coordinate_sets{area, set_number}.description := "";
        coordinate_sets{area, set_number}.valid := FALSE;
        coordinate_sets{area, set_number}.created_time := 0;
        coordinate_sets{area, set_number}.last_executed_time := 0;
        
        ! Reset coordinates to safe default
        FOR coord FROM 1 TO 10 DO
            coordinate_sets{area, set_number}.coordinates{coord} := [[0, 0, 300], [1, 0, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
        ENDFOR
        
        TPWrite "Coordinate set [" + NumToStr(area, 0) + "," + NumToStr(set_number, 0) + "] cleared";
    ENDPROC
    
    !***************************************************************************
    ! PROC Print_Coordinate_Set_Info
    ! Print information about coordinate set
    !***************************************************************************
    PROC Print_Coordinate_Set_Info(num area, num set_number)
        ! Validate inputs
        IF area < 1 OR area > MAX_AREAS THEN
            TPWrite "Invalid area: " + NumToStr(area, 0);
            RETURN;
        ENDIF
        
        IF set_number < 1 OR set_number > MAX_COORDINATE_SETS THEN
            TPWrite "Invalid set number: " + NumToStr(set_number, 0);
            RETURN;
        ENDIF
        
        ! Print coordinate set information
        TPWrite "=== Coordinate Set Info ===";
        TPWrite "Area: " + NumToStr(area, 0);
        TPWrite "Set Number: " + NumToStr(set_number, 0);
        TPWrite "Description: " + coordinate_sets{area, set_number}.description;
        TPWrite "Coordinate Count: " + NumToStr(coordinate_sets{area, set_number}.coordinate_count, 0);
        TPWrite "Valid: " + BoolToStr(coordinate_sets{area, set_number}.valid);
        TPWrite "Created Time: " + NumToStr(coordinate_sets{area, set_number}.created_time, 0);
        TPWrite "Last Executed: " + NumToStr(coordinate_sets{area, set_number}.last_executed_time, 0);
        TPWrite "========================";
    ENDPROC
    
    !***************************************************************************
    ! PROC Print_System_Status
    ! Print system status information
    !***************************************************************************
    PROC Print_System_Status()
        TPWrite "=== Coordinate Handler Status ===";
        TPWrite "Initialized: " + BoolToStr(coordinate_handler_initialized);
        TPWrite "Validation Errors: " + NumToStr(validation_errors, 0);
        TPWrite "Last Validation: " + NumToStr(last_validation_time, 0);
        TPWrite "Safety Zones: " + NumToStr(safety_zone_count, 0);
        TPWrite "Work Areas Active: " + BoolToStr(work_areas{1}.active) + ", " + BoolToStr(work_areas{2}.active);
        TPWrite "==============================";
    ENDPROC
    
ENDMODULE
