#!/usr/bin/env python3
"""
GUI Interface for PC-PLC-Robot Communication
=============================================

Description: Graphical user interface for coordinate management and robot control
Purpose: User-friendly interface for laptop-side coordinate exchange system
Framework: tkinter (built-in Python GUI library)
Version: 1.0
Date: 17/07/2025

Features:
- Coordinate input and management
- Real-time PLC communication
- Robot status monitoring
- Error handling and display
- Configuration management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

from plc_client import PLCClient
from coordinate_manager import CoordinateManager, Coordinate, CoordinateSet
from data_validator import DataValidator

class PLCRobotGUI:
    """
    Main GUI Application for PC-PLC-Robot Communication
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize GUI application
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("PC-PLC-Robot Communication System")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.plc_client = None
        self.coord_manager = None
        self.validator = DataValidator()
        self.connected = False
        self.monitoring = False
        self.monitor_thread = None
        
        # Connection settings
        self.plc_ip = tk.StringVar(value="192.168.1.100")
        self.plc_rack = tk.IntVar(value=0)
        self.plc_slot = tk.IntVar(value=2)
        
        # Current selections
        self.current_area = tk.IntVar(value=1)
        self.current_set = tk.IntVar(value=1)
        
        # Create GUI elements
        self.create_widgets()
        
        # Status variables
        self.status_text = tk.StringVar(value="Disconnected")
        self.robot_status = tk.StringVar(value="Unknown")
        self.last_update = tk.StringVar(value="Never")
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_connection_tab()
        self.create_coordinate_tab()
        self.create_control_tab()
        self.create_monitor_tab()
        self.create_config_tab()
        
        # Create status bar
        self.create_status_bar()
    
    def create_connection_tab(self):
        """Create connection configuration tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Connection")
        
        # Connection settings
        settings_frame = ttk.LabelFrame(frame, text="PLC Connection Settings")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(settings_frame, text="PLC IP Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.plc_ip, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Rack:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.plc_rack, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Slot:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.plc_slot, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        # Connection buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.connect_button = ttk.Button(button_frame, text="Connect", command=self.connect_plc)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_button = ttk.Button(button_frame, text="Disconnect", command=self.disconnect_plc, state=tk.DISABLED)
        self.disconnect_button.pack(side=tk.LEFT, padx=5)
        
        # Connection status
        status_frame = ttk.LabelFrame(frame, text="Connection Status")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(status_frame, textvariable=self.status_text).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(status_frame, text="Last Update:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(status_frame, textvariable=self.last_update).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    
    def create_coordinate_tab(self):
        """Create coordinate management tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Coordinates")
        
        # Area and set selection
        selection_frame = ttk.LabelFrame(frame, text="Area and Set Selection")
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(selection_frame, text="Area:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        area_combo = ttk.Combobox(selection_frame, textvariable=self.current_area, values=[1, 2], width=10)
        area_combo.grid(row=0, column=1, padx=5, pady=5)
        area_combo.bind('<<ComboboxSelected>>', self.on_area_changed)
        
        ttk.Label(selection_frame, text="Set:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        set_combo = ttk.Combobox(selection_frame, textvariable=self.current_set, values=list(range(1, 11)), width=10)
        set_combo.grid(row=0, column=3, padx=5, pady=5)
        set_combo.bind('<<ComboboxSelected>>', self.on_set_changed)
        
        # Coordinate input
        input_frame = ttk.LabelFrame(frame, text="Coordinate Input")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Position inputs
        self.x_var = tk.IntVar(value=0)
        self.y_var = tk.IntVar(value=0)
        self.z_var = tk.IntVar(value=300)
        self.rx_var = tk.IntVar(value=0)
        self.ry_var = tk.IntVar(value=0)
        self.rz_var = tk.IntVar(value=0)
        self.gripper_var = tk.IntVar(value=0)
        self.speed_var = tk.IntVar(value=50)
        
        # Position frame
        pos_frame = ttk.Frame(input_frame)
        pos_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        ttk.Label(pos_frame, text="X:").grid(row=0, column=0, padx=5)
        ttk.Entry(pos_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(pos_frame, text="Y:").grid(row=0, column=2, padx=5)
        ttk.Entry(pos_frame, textvariable=self.y_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(pos_frame, text="Z:").grid(row=0, column=4, padx=5)
        ttk.Entry(pos_frame, textvariable=self.z_var, width=10).grid(row=0, column=5, padx=5)
        
        # Rotation frame
        rot_frame = ttk.Frame(input_frame)
        rot_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        ttk.Label(rot_frame, text="RX:").grid(row=0, column=0, padx=5)
        ttk.Entry(rot_frame, textvariable=self.rx_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(rot_frame, text="RY:").grid(row=0, column=2, padx=5)
        ttk.Entry(rot_frame, textvariable=self.ry_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(rot_frame, text="RZ:").grid(row=0, column=4, padx=5)
        ttk.Entry(rot_frame, textvariable=self.rz_var, width=10).grid(row=0, column=5, padx=5)
        
        # Control frame
        control_frame = ttk.Frame(input_frame)
        control_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        ttk.Label(control_frame, text="Gripper:").grid(row=0, column=0, padx=5)
        gripper_combo = ttk.Combobox(control_frame, textvariable=self.gripper_var, values=[0, 1], width=10)
        gripper_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Speed:").grid(row=0, column=2, padx=5)
        ttk.Entry(control_frame, textvariable=self.speed_var, width=10).grid(row=0, column=3, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Validate", command=self.validate_coordinate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Set", command=self.save_coordinate_set).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Set", command=self.load_coordinate_set).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Get Current", command=self.get_current_position).pack(side=tk.LEFT, padx=5)
        
        # Coordinate sets list
        list_frame = ttk.LabelFrame(frame, text="Coordinate Sets")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for coordinate sets
        self.coord_tree = ttk.Treeview(list_frame, columns=('Area', 'Set', 'X', 'Y', 'Z', 'Description'), show='headings')
        self.coord_tree.heading('Area', text='Area')
        self.coord_tree.heading('Set', text='Set')
        self.coord_tree.heading('X', text='X')
        self.coord_tree.heading('Y', text='Y')
        self.coord_tree.heading('Z', text='Z')
        self.coord_tree.heading('Description', text='Description')
        
        # Configure column widths
        self.coord_tree.column('Area', width=50)
        self.coord_tree.column('Set', width=50)
        self.coord_tree.column('X', width=80)
        self.coord_tree.column('Y', width=80)
        self.coord_tree.column('Z', width=80)
        self.coord_tree.column('Description', width=200)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.coord_tree.yview)
        self.coord_tree.configure(yscrollcommand=scrollbar.set)
        
        self.coord_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.coord_tree.bind('<Double-1>', self.on_coordinate_double_click)
    
    def create_control_tab(self):
        """Create robot control tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Control")
        
        # Execution control
        exec_frame = ttk.LabelFrame(frame, text="Execution Control")
        exec_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(exec_frame, text="Write to PLC", command=self.write_to_plc).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(exec_frame, text="Execute Set", command=self.execute_coordinate_set).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(exec_frame, text="Get Position", command=self.get_current_position).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Emergency controls
        emergency_frame = ttk.LabelFrame(frame, text="Emergency Controls")
        emergency_frame.pack(fill=tk.X, padx=10, pady=10)
        
        emergency_button = ttk.Button(emergency_frame, text="EMERGENCY STOP", command=self.emergency_stop)
        emergency_button.pack(side=tk.LEFT, padx=5, pady=5)
        emergency_button.configure(style='Emergency.TButton')
        
        ttk.Button(emergency_frame, text="Reset Error", command=self.reset_error).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(emergency_frame, text="Stop Motion", command=self.stop_motion).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Current position display
        pos_frame = ttk.LabelFrame(frame, text="Current Position")
        pos_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.current_pos_text = tk.Text(pos_frame, height=6, width=60, state=tk.DISABLED)
        self.current_pos_text.pack(padx=5, pady=5)
        
        # Log display
        log_frame = ttk.LabelFrame(frame, text="Operation Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(log_frame, height=15, width=80, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_monitor_tab(self):
        """Create monitoring tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Monitor")
        
        # Monitoring controls
        monitor_frame = ttk.LabelFrame(frame, text="Monitoring Controls")
        monitor_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.monitor_button = ttk.Button(monitor_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.monitor_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(monitor_frame, text="Refresh", command=self.refresh_status).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status displays
        status_frame = ttk.LabelFrame(frame, text="System Status")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # PLC status
        ttk.Label(status_frame, text="PLC Status:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.plc_status_label = ttk.Label(status_frame, text="Unknown")
        self.plc_status_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Robot status
        ttk.Label(status_frame, text="Robot Status:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.robot_status_label = ttk.Label(status_frame, textvariable=self.robot_status)
        self.robot_status_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Data blocks display
        db_frame = ttk.LabelFrame(frame, text="Data Blocks")
        db_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for data blocks
        self.db_notebook = ttk.Notebook(db_frame)
        self.db_notebook.pack(fill=tk.BOTH, expand=True)
        
        # DB100 display
        self.db100_text = tk.Text(self.db_notebook, height=15, state=tk.DISABLED)
        self.db_notebook.add(self.db100_text, text="DB100 (Laptop)")
        
        # DB101 display
        self.db101_text = tk.Text(self.db_notebook, height=15, state=tk.DISABLED)
        self.db_notebook.add(self.db101_text, text="DB101 (Robot)")
    
    def create_config_tab(self):
        """Create configuration tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Configuration")
        
        # File operations
        file_frame = ttk.LabelFrame(frame, text="File Operations")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(file_frame, text="Import CSV", command=self.import_coordinates).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(file_frame, text="Export CSV", command=self.export_coordinates).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(file_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(file_frame, text="Load Config", command=self.load_config).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Validation settings
        validation_frame = ttk.LabelFrame(frame, text="Validation Settings")
        validation_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(validation_frame, text="Edit Validation Config", command=self.edit_validation_config).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(validation_frame, text="Test Validation", command=self.test_validation).pack(side=tk.LEFT, padx=5, pady=5)
        
        # System information
        info_frame = ttk.LabelFrame(frame, text="System Information")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.info_text = tk.Text(info_frame, height=20, state=tk.DISABLED)
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load system info
        self.load_system_info()
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, textvariable=self.status_text, relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = ttk.Label(self.status_bar, text="", relief=tk.SUNKEN)
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        # Update time
        self.update_time()
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def connect_plc(self):
        """Connect to PLC"""
        try:
            self.plc_client = PLCClient(self.plc_ip.get(), self.plc_rack.get(), self.plc_slot.get())
            if self.plc_client.connect():
                self.coord_manager = CoordinateManager(self.plc_client)
                self.connected = True
                self.status_text.set("Connected")
                self.connect_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.NORMAL)
                self.last_update.set(datetime.now().strftime("%H:%M:%S"))
                self.log_message("Connected to PLC successfully")
                self.refresh_coordinate_list()
            else:
                messagebox.showerror("Connection Error", "Failed to connect to PLC")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Connection failed: {str(e)}")
    
    def disconnect_plc(self):
        """Disconnect from PLC"""
        if self.plc_client:
            self.plc_client.disconnect()
            self.connected = False
            self.status_text.set("Disconnected")
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.log_message("Disconnected from PLC")
            if self.monitoring:
                self.toggle_monitoring()
    
    def validate_coordinate(self):
        """Validate current coordinate input"""
        try:
            result = self.validator.validate_coordinate(
                self.x_var.get(), self.y_var.get(), self.z_var.get(),
                self.rx_var.get(), self.ry_var.get(), self.rz_var.get(),
                self.current_area.get()
            )
            
            report = self.validator.get_validation_report(result)
            
            if result.is_valid:
                messagebox.showinfo("Validation", report)
            else:
                messagebox.showerror("Validation Error", report)
                
        except Exception as e:
            messagebox.showerror("Validation Error", f"Validation failed: {str(e)}")
    
    def save_coordinate_set(self):
        """Save current coordinate as set"""
        if not self.coord_manager:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        try:
            # Get description from user
            description = simpledialog.askstring("Description", "Enter description for coordinate set:")
            if description is None:
                return
            
            coord = Coordinate(
                x=self.x_var.get(),
                y=self.y_var.get(),
                z=self.z_var.get(),
                rx=self.rx_var.get(),
                ry=self.ry_var.get(),
                rz=self.rz_var.get(),
                gripper=self.gripper_var.get(),
                speed=self.speed_var.get()
            )
            
            coord_set = CoordinateSet(
                area=self.current_area.get(),
                set_number=self.current_set.get(),
                coordinates=[coord],
                description=description
            )
            
            if self.coord_manager.add_coordinate_set(coord_set):
                messagebox.showinfo("Success", "Coordinate set saved successfully")
                self.refresh_coordinate_list()
                self.log_message(f"Saved coordinate set {self.current_set.get()} for area {self.current_area.get()}")
            else:
                messagebox.showerror("Error", "Failed to save coordinate set")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save coordinate set: {str(e)}")
    
    def load_coordinate_set(self):
        """Load coordinate set from manager"""
        if not self.coord_manager:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        try:
            coord_set = self.coord_manager.get_coordinate_set(self.current_area.get(), self.current_set.get())
            if coord_set and coord_set.coordinates:
                coord = coord_set.coordinates[0]
                self.x_var.set(coord.x)
                self.y_var.set(coord.y)
                self.z_var.set(coord.z)
                self.rx_var.set(coord.rx)
                self.ry_var.set(coord.ry)
                self.rz_var.set(coord.rz)
                self.gripper_var.set(coord.gripper)
                self.speed_var.set(coord.speed)
                
                self.log_message(f"Loaded coordinate set {self.current_set.get()} from area {self.current_area.get()}")
            else:
                messagebox.showinfo("Info", "No coordinate set found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load coordinate set: {str(e)}")
    
    def write_to_plc(self):
        """Write current coordinate to PLC"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        try:
            success = self.plc_client.write_coordinate_set(
                area=self.current_area.get(),
                set_number=self.current_set.get(),
                x=self.x_var.get(),
                y=self.y_var.get(),
                z=self.z_var.get(),
                rx=self.rx_var.get(),
                ry=self.ry_var.get(),
                rz=self.rz_var.get(),
                gripper=self.gripper_var.get(),
                speed=self.speed_var.get()
            )
            
            if success:
                messagebox.showinfo("Success", "Coordinate written to PLC")
                self.log_message(f"Written coordinate set {self.current_set.get()} to PLC")
            else:
                messagebox.showerror("Error", "Failed to write coordinate to PLC")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write to PLC: {str(e)}")
    
    def execute_coordinate_set(self):
        """Execute coordinate set"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        try:
            success = self.plc_client.execute_coordinate_set(
                area=self.current_area.get(),
                set_number=self.current_set.get()
            )
            
            if success:
                messagebox.showinfo("Success", "Coordinate set executed")
                self.log_message(f"Executed coordinate set {self.current_set.get()}")
            else:
                messagebox.showerror("Error", "Failed to execute coordinate set")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute coordinate set: {str(e)}")
    
    def get_current_position(self):
        """Get current robot position"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        try:
            position = self.plc_client.get_current_position()
            if position:
                # Update display
                self.current_pos_text.config(state=tk.NORMAL)
                self.current_pos_text.delete(1.0, tk.END)
                self.current_pos_text.insert(tk.END, f"X: {position['x']}\n")
                self.current_pos_text.insert(tk.END, f"Y: {position['y']}\n")
                self.current_pos_text.insert(tk.END, f"Z: {position['z']}\n")
                self.current_pos_text.insert(tk.END, f"RX: {position['rx']}\n")
                self.current_pos_text.insert(tk.END, f"RY: {position['ry']}\n")
                self.current_pos_text.insert(tk.END, f"RZ: {position['rz']}\n")
                self.current_pos_text.insert(tk.END, f"Gripper: {position['gripper']}\n")
                self.current_pos_text.config(state=tk.DISABLED)
                
                self.log_message("Retrieved current position")
            else:
                messagebox.showerror("Error", "Failed to get current position")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get current position: {str(e)}")
    
    def emergency_stop(self):
        """Send emergency stop command"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        try:
            success = self.plc_client.emergency_stop()
            if success:
                messagebox.showwarning("Emergency Stop", "Emergency stop command sent")
                self.log_message("EMERGENCY STOP command sent")
            else:
                messagebox.showerror("Error", "Failed to send emergency stop")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send emergency stop: {str(e)}")
    
    def reset_error(self):
        """Reset error state"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        try:
            success = self.plc_client.reset_error()
            if success:
                messagebox.showinfo("Success", "Error reset successful")
                self.log_message("Error reset successful")
            else:
                messagebox.showerror("Error", "Failed to reset error")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset error: {str(e)}")
    
    def stop_motion(self):
        """Stop robot motion"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        try:
            success = self.plc_client.send_command('STOP_MOTION')
            if success:
                messagebox.showinfo("Success", "Motion stopped")
                self.log_message("Motion stop command sent")
            else:
                messagebox.showerror("Error", "Failed to stop motion")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop motion: {str(e)}")
    
    def toggle_monitoring(self):
        """Toggle monitoring"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        if self.monitoring:
            self.monitoring = False
            self.monitor_button.config(text="Start Monitoring")
            self.log_message("Monitoring stopped")
        else:
            self.monitoring = True
            self.monitor_button.config(text="Stop Monitoring")
            self.log_message("Monitoring started")
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def monitor_loop(self):
        """Monitoring loop"""
        while self.monitoring and self.connected:
            try:
                # Read data blocks
                db100 = self.plc_client.read_db100()
                db101 = self.plc_client.read_db101()
                
                # Update displays
                self.root.after(0, self.update_db_displays, db100, db101)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                self.log_message(f"Monitoring error: {str(e)}")
                time.sleep(2)
    
    def update_db_displays(self, db100, db101):
        """Update data block displays"""
        # Update DB100
        self.db100_text.config(state=tk.NORMAL)
        self.db100_text.delete(1.0, tk.END)
        for key, value in db100.items():
            self.db100_text.insert(tk.END, f"{key}: {value}\n")
        self.db100_text.config(state=tk.DISABLED)
        
        # Update DB101
        self.db101_text.config(state=tk.NORMAL)
        self.db101_text.delete(1.0, tk.END)
        for key, value in db101.items():
            self.db101_text.insert(tk.END, f"{key}: {value}\n")
        self.db101_text.config(state=tk.DISABLED)
        
        # Update status
        self.robot_status.set(f"Status: {db101.get('robot_status', 'Unknown')}")
    
    def refresh_status(self):
        """Refresh status displays"""
        if self.connected:
            self.get_current_position()
            self.last_update.set(datetime.now().strftime("%H:%M:%S"))
    
    def refresh_coordinate_list(self):
        """Refresh coordinate list"""
        if not self.coord_manager:
            return
        
        # Clear existing items
        for item in self.coord_tree.get_children():
            self.coord_tree.delete(item)
        
        # Add coordinate sets
        coord_sets = self.coord_manager.list_coordinate_sets()
        for coord_set in coord_sets:
            if coord_set.coordinates:
                coord = coord_set.coordinates[0]
                self.coord_tree.insert('', 'end', values=(
                    coord_set.area,
                    coord_set.set_number,
                    coord.x,
                    coord.y,
                    coord.z,
                    coord_set.description
                ))
    
    def on_area_changed(self, event):
        """Handle area selection change"""
        self.refresh_coordinate_list()
    
    def on_set_changed(self, event):
        """Handle set selection change"""
        pass
    
    def on_coordinate_double_click(self, event):
        """Handle coordinate double-click"""
        selection = self.coord_tree.selection()
        if selection:
            item = self.coord_tree.item(selection[0])
            values = item['values']
            
            # Load coordinate into input fields
            self.current_area.set(values[0])
            self.current_set.set(values[1])
            self.x_var.set(values[2])
            self.y_var.set(values[3])
            self.z_var.set(values[4])
    
    def import_coordinates(self):
        """Import coordinates from CSV file"""
        if not self.coord_manager:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        file_path = filedialog.askopenfilename(
            title="Import Coordinates",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                success = self.coord_manager.import_coordinates_from_file(file_path)
                if success:
                    messagebox.showinfo("Success", "Coordinates imported successfully")
                    self.refresh_coordinate_list()
                else:
                    messagebox.showerror("Error", "Failed to import coordinates")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    def export_coordinates(self):
        """Export coordinates to CSV file"""
        if not self.coord_manager:
            messagebox.showerror("Error", "Not connected to PLC")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Coordinates",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                success = self.coord_manager.export_coordinates_to_file(file_path)
                if success:
                    messagebox.showinfo("Success", "Coordinates exported successfully")
                else:
                    messagebox.showerror("Error", "Failed to export coordinates")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def save_config(self):
        """Save configuration"""
        config = {
            'plc_ip': self.plc_ip.get(),
            'plc_rack': self.plc_rack.get(),
            'plc_slot': self.plc_slot.get(),
            'current_area': self.current_area.get(),
            'current_set': self.current_set.get()
        }
        
        try:
            with open('gui_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        """Load configuration"""
        try:
            with open('gui_config.json', 'r') as f:
                config = json.load(f)
            
            self.plc_ip.set(config.get('plc_ip', '192.168.1.100'))
            self.plc_rack.set(config.get('plc_rack', 0))
            self.plc_slot.set(config.get('plc_slot', 2))
            self.current_area.set(config.get('current_area', 1))
            self.current_set.set(config.get('current_set', 1))
            
            messagebox.showinfo("Success", "Configuration loaded")
        except Exception as e:
            messagebox.showinfo("Info", "No configuration file found, using defaults")
    
    def edit_validation_config(self):
        """Edit validation configuration"""
        messagebox.showinfo("Info", "Validation configuration editing not implemented yet")
    
    def test_validation(self):
        """Test validation with current input"""
        self.validate_coordinate()
    
    def load_system_info(self):
        """Load system information"""
        info = f"""PC-PLC-Robot Communication System
Version: 1.0
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

System Components:
- PLC Client: Siemens S7-400H communication
- Coordinate Manager: Coordinate set management
- Data Validator: Input validation and safety checks
- GUI Interface: tkinter-based user interface

Configuration Files:
- gui_config.json: GUI settings
- coordinate_config.json: Coordinate manager settings
- validation_config.json: Validation rules
- coordinate_sets.json: Saved coordinate sets

Network Configuration:
- PLC IP: {self.plc_ip.get()}
- Rack: {self.plc_rack.get()}
- Slot: {self.plc_slot.get()}

Status: {'Connected' if self.connected else 'Disconnected'}
"""
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)
    
    def log_message(self, message: str):
        """Log message to operation log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Handle window closing"""
        if self.monitoring:
            self.monitoring = False
        
        if self.connected:
            self.disconnect_plc()
        
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    
    # Configure styles
    style = ttk.Style()
    style.configure('Emergency.TButton', foreground='red')
    
    # Create application
    app = PLCRobotGUI(root)
    
    # Try to load configuration
    app.load_config()
    
    # Start GUI
    root.mainloop()

if __name__ == "__main__":
    main()
