import sys
import time
import numpy as np
import serial  # For serial communication
import subprocess  # For running external scripts
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QGridLayout, QFrame
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer

# Add this import for the AnimatedToggle
from animated_toggle import AnimatedToggle  # Save the AnimatedToggle class in a file named animated_toggle.py


class SmartHomeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Home Control Panel")
        self.setGeometry(500, 100, 400, 600)
        self.setStyleSheet("background-color:white;")

        # Initialize Serial Communication
        try:
            self.serial_port = serial.Serial('COM6', 9600, timeout=1)  # Replace 'COM3' with your Arduino's port
        except serial.SerialException:
            print("Error: Could not open serial port.")
            self.serial_port = None

        # Main Widget
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: white;")
        self.setCentralWidget(main_widget)

        # Main Layout
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Header Section
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #ff7f50; border-radius: 100px;")
        header_layout = QHBoxLayout()
        header_frame.setLayout(header_layout)

        profile_pic = QLabel()
        profile_pixmap = QPixmap(r"A:\College stuff\DATA AQ\Nour1.jpg")
        if profile_pixmap.isNull():
            print("Error: profile.jpg not found.")
        profile_pixmap = profile_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        profile_pic.setPixmap(profile_pixmap)
        profile_pic.setStyleSheet("border-radius: 50px;")
        header_layout.addWidget(profile_pic)

        welcome_label = QLabel("Welcome Home,\nNour El Din Nassar")
        welcome_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(welcome_label)

        self.temp_label = QLabel("Temperature: --°C")
        self.temp_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(self.temp_label, alignment=Qt.AlignRight)

        self.humidity_label = QLabel("Humidity: --%")
        self.humidity_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(self.humidity_label, alignment=Qt.AlignRight)

        main_layout.addWidget(header_frame)

        # Rooms Section
        rooms_label = QLabel("Rooms")
        rooms_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px 0;")
        main_layout.addWidget(rooms_label)

        rooms_layout = QHBoxLayout()
        room_buttons = [
            {"name": "Living Room", "icon": r"A:\College stuff\DATA AQ\GUI\icons\living-room.jpg"},
            {"name": "Kitchen", "icon": r"A:\College stuff\DATA AQ\GUI\icons\kitchen.jpg"},
            {"name": "Garage", "icon": r"A:\College stuff\DATA AQ\GUI\icons\garage.jpg"},
            {"name": "Bedroom", "icon": r"A:\College stuff\DATA AQ\GUI\icons\bedroom.jpg"},
            {"name": "Gym", "icon": r"A:\College stuff\DATA AQ\GUI\icons\gym.jpg"}

        ]

        self.active_room_button = None  # Track the currently active room button

        for i, room in enumerate(room_buttons):
            room_button = QPushButton(room["name"])
            room_button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {'#ff7f50' if i == 0 else 'white'};
                    color: {'white' if i == 0 else 'black'};
                    border: 1px solid #ff7f50;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: #ff5722;
                }}
                """
            )
            room_icon_pixmap = QPixmap(room["icon"]).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            room_icon = QIcon(room_icon_pixmap)
            room_button.setIcon(room_icon)
            room_button.setIconSize(room_icon_pixmap.size())

            # Connect each button to the slot to handle clicks
            room_button.clicked.connect(lambda checked, b=room_button, r=room["name"]: self.handle_room_button_click(b, r))

            rooms_layout.addWidget(room_button)

            # Set the first button (Living Room) as active by default
            if i == 0:
                self.active_room_button = room_button

        main_layout.addLayout(rooms_layout)

        # Devices Section
        devices_label = QLabel("Functionalities")
        devices_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px 0;")
        main_layout.addWidget(devices_label)

        self.devices_layout = QGridLayout()
        devices = [
            {"name": "Air Conditioner", "icon": r"A:\College stuff\DATA AQ\GUI\icons\airconditioner.jpg"},
            {"name": "Bulb Lamp", "icon": r"A:\College stuff\DATA AQ\GUI\icons\light.jpg"}
        ]

        self.device_frames = {}  # Save device frames here!

        for i, device in enumerate(devices):
            device_frame = QFrame()
            device_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
            device_layout = QVBoxLayout()
            device_frame.setLayout(device_layout)

            icon_label = QLabel()
            icon_pixmap = QPixmap(device["icon"]).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if icon_pixmap.isNull():
                print(f"Error: {device['icon']} not found.")
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            device_layout.addWidget(icon_label)

            name_label = QLabel(device["name"])
            name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
            name_label.setAlignment(Qt.AlignCenter)
            device_layout.addWidget(name_label)

            # Add the animated toggle button
            toggle_button_layout = QHBoxLayout()
            toggle_button_layout.addStretch()
            toggle_button = AnimatedToggle()
            toggle_button_layout.addWidget(toggle_button)
            toggle_button_layout.addStretch()
            device_layout.addLayout(toggle_button_layout)

            # Save the frame reference
            self.device_frames[device["name"]] = device_frame

            self.devices_layout.addWidget(device_frame, i // 2, i % 2)
        # Add Gate 1 Section
        gate1_frame = QFrame()
        gate1_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        gate1_layout = QVBoxLayout()
        gate1_frame.setLayout(gate1_layout)

        # Add Gate 1 Icon
        gate1_icon_label = QLabel()
        gate1_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\gate.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if gate1_pixmap.isNull():
            print("Error: gate.jpg not found.")
            gate1_icon_label.setText("No Image")
        else:
            gate1_icon_label.setPixmap(gate1_pixmap)
        gate1_icon_label.setAlignment(Qt.AlignCenter)
        gate1_layout.addWidget(gate1_icon_label)

        # Add Gate 1 Label
        gate1_name_label = QLabel("Gate")
        gate1_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        gate1_name_label.setAlignment(Qt.AlignCenter)
        gate1_layout.addWidget(gate1_name_label)  # Correct - adds the name label

        # Add Gate 1 Toggle Button
        gate1_toggle_layout = QHBoxLayout()
        gate1_toggle_layout.addStretch()
        gate1_toggle = AnimatedToggle()
        gate1_toggle.setFixedSize(50, 25)
        gate1_toggle.stateChanged.connect(lambda state: self.handle_gate_toggle(state, "Gate"))  # Connect to a handler
        gate1_toggle_layout.addWidget(gate1_toggle)
        gate1_toggle_layout.addStretch()
        gate1_layout.addLayout(gate1_toggle_layout)

        # Add Gate 1 Frame to Devices Layout
        self.devices_layout.addWidget(gate1_frame, 1, 0)  # Place in row 1, column 0
        self.device_frames["Gate 1"] = gate1_frame

        # Add Face ID Section (replacing Gate 2)
        faceid_frame = QFrame()
        faceid_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        faceid_layout = QVBoxLayout()
        faceid_frame.setLayout(faceid_layout)

        # Add Face ID Icon
        faceid_icon_label = QLabel()
        faceid_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\FaceID.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if faceid_pixmap.isNull():
            print("Error: Face ID image not found.")
            faceid_icon_label.setText("No Image")
        else:
            faceid_icon_label.setPixmap(faceid_pixmap)
        faceid_icon_label.setAlignment(Qt.AlignCenter)
        faceid_layout.addWidget(faceid_icon_label)

        # Add Face ID Label
        faceid_name_label = QLabel("Open Main Door")
        faceid_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        faceid_name_label.setAlignment(Qt.AlignCenter)
        faceid_layout.addWidget(faceid_name_label)

        # Add Face ID Button (not toggle)
        faceid_button_layout = QHBoxLayout()
        faceid_button_layout.addStretch()
        faceid_button = QPushButton("Verify")
        faceid_button.setStyleSheet("""
            QPushButton {
                background-color: #ff7f50;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5722;
            }
        """)
        faceid_button.clicked.connect(self.handle_faceid_button)
        faceid_button_layout.addWidget(faceid_button)

        # Add a small spacing between buttons
        faceid_button_layout.addSpacing(10)

        # Add Close Main Door button
        close_maindoor_button = QPushButton("Close")
        close_maindoor_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e64a19;
            }
        """)
        close_maindoor_button.clicked.connect(self.handle_close_maindoor_button)
        faceid_button_layout.addWidget(close_maindoor_button)

        faceid_button_layout.addStretch()
        faceid_layout.addLayout(faceid_button_layout)

        # Add Face ID Frame to Devices Layout
        self.devices_layout.addWidget(faceid_frame, 1, 1)  # Place in row 1, column 1
        self.device_frames["Face ID"] = faceid_frame

        main_layout.addLayout(self.devices_layout)

        # Timer to Update Sensor Data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor_data)
        self.timer.start(2000)  # Update every 2 seconds

    def update_sensor_data(self):
        if self.serial_port:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    print(f"Serial Data: {line}")
                    if "Temperature:" in line and "Humidity:" in line:
                        # Extract temperature and humidity values
                        temp_start = line.find("Temperature:") + len("Temperature:")
                        temp_end = line.find("C")
                        temp = line[temp_start:temp_end].strip()

                        humidity_start = line.find("Humidity:") + len("Humidity:")
                        humidity_end = line.find("%")
                        humidity = line[humidity_start:humidity_end].strip()

                        # Update the labels
                        self.temp_label.setText(f"Temperature: {temp}°C")
                        self.humidity_label.setText(f"Humidity: {humidity}%")
                    
                    # Add this code to handle garage door state messages
                    elif "GarageState:" in line:
                        state = line.split("GarageState:")[1].strip()
                        # Update garage door toggle if it exists in the current view
                        if "Garage Door" in self.device_frames:
                            garage_frame = self.device_frames["Garage Door"]
                            # Find the toggle button in the frame's layout
                            for i in range(garage_frame.layout().count()):
                                item = garage_frame.layout().itemAt(i)
                                if isinstance(item, QHBoxLayout):
                                    for j in range(item.count()):
                                        widget = item.itemAt(j).widget()
                                        if isinstance(widget, AnimatedToggle):
                                            widget.blockSignals(True)  # Prevent toggle from sending commands
                                            widget.setChecked(state == "OPEN")
                                            widget.blockSignals(False)
                                            break
            except Exception as e:
                print(f"Error reading serial data: {e}")

    def handle_room_button_click(self, clicked_button, room_name):
        # Reset the style of the previously active button
        if self.active_room_button:
            self.active_room_button.setStyleSheet(
                """
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid #ff7f50;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #ff5722;
                }
                """
            )

        # Set the style of the clicked button
        clicked_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ff7f50;
                color: white;
                border: 1px solid #ff7f50;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #ff5722;
            }
            """
        )

        # Update the active button
        self.active_room_button = clicked_button

        # Call the appropriate functionality based on the room
        if room_name == "Garage":
            self.show_garage_functionalities()
        elif room_name == "Living Room":
            self.show_living_room_functionalities()
        elif room_name == "Kitchen":
            self.show_kitchen_functionalities()
        elif room_name == "Bedroom":
            self.show_bedroom_functionalities()
        elif room_name == "Gym":
            self.show_gym_functionalities()
    def handle_garage_door_toggle(self, state):
        """Handle the toggle state of the Garage Door."""
        if state:
            print("Garage Door is now OPEN.")
            # Send command to Arduino
            if self.serial_port:
                try:
                    self.serial_port.write(b"OPENGARAGEDOOR\n")
                    print("[SERIAL] Sent: OPENGARAGEDOOR")
                except Exception as e:
                    print(f"Error sending garage door command: {e}")
        else:
            print("Garage Door is now CLOSED.")
            # Send command to Arduino
            if self.serial_port:
                try:
                    self.serial_port.write(b"CLOSEGARAGEDOOR\n")  # Added missing newline
                    print("[SERIAL] Sent: CLOSEGARAGEDOOR")
                except Exception as e:
                    print(f"Error sending garage door command: {e}")

    def show_garage_functionalities(self):
        """Display functionalities for the Garage."""
        print("Garage functionalities displayed.")
        
        # Clear existing devices first
        while self.devices_layout.count():
            child = self.devices_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.device_frames.clear()  # Clear the device_frames dictionary

        # Create Garage Door Frame
        garage_door_frame = QFrame()
        garage_door_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        garage_door_layout = QVBoxLayout()
        garage_door_frame.setLayout(garage_door_layout)

        # Add Garage Door Photo
        garage_door_icon_label = QLabel()
        garage_door_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\garage.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        garage_door_icon_label.setPixmap(garage_door_pixmap)
        garage_door_icon_label.setAlignment(Qt.AlignCenter)
        garage_door_layout.addWidget(garage_door_icon_label)

        # Add Garage Door Name
        garage_door_name_label = QLabel("Garage Door")
        garage_door_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        garage_door_name_label.setAlignment(Qt.AlignCenter)
        garage_door_layout.addWidget(garage_door_name_label)

        # Add Garage Door Toggle Button
        garage_door_toggle_layout = QHBoxLayout()
        garage_door_toggle_layout.addStretch()
        garage_door_toggle = AnimatedToggle()
        garage_door_toggle.setFixedSize(50, 25)
        garage_door_toggle.stateChanged.connect(self.handle_garage_door_toggle)
        garage_door_toggle_layout.addWidget(garage_door_toggle)
        garage_door_toggle_layout.addStretch()
        garage_door_layout.addLayout(garage_door_toggle_layout)

        self.devices_layout.addWidget(garage_door_frame, 0, 0)
        self.device_frames["Garage Door"] = garage_door_frame

        # Create Light Frame
        light_frame = QFrame()
        light_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        light_layout = QVBoxLayout()
        light_frame.setLayout(light_layout)

        light_icon_label = QLabel()
        light_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\light.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        light_icon_label.setPixmap(light_pixmap)
        light_icon_label.setAlignment(Qt.AlignCenter)
        light_layout.addWidget(light_icon_label)

        light_name_label = QLabel("Garage Light")
        light_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        light_name_label.setAlignment(Qt.AlignCenter)
        light_layout.addWidget(light_name_label)

        light_toggle_layout = QHBoxLayout()
        light_toggle_layout.addStretch()
        light_toggle = AnimatedToggle()
        light_toggle.stateChanged.connect(self.handle_garage_light_toggle)  # Add this line
        light_toggle_layout.addWidget(light_toggle)
        light_toggle_layout.addStretch()
        light_layout.addLayout(light_toggle_layout)

        self.devices_layout.addWidget(light_frame, 0, 1)
        self.device_frames["Garage Light"] = light_frame
        
        # Request current garage door state
        if self.serial_port:
            try:
                self.serial_port.write(b"GET_STATE\n")
                print("[SERIAL] Requested garage door state")
            except Exception as e:
                print(f"Error requesting device state: {e}")

        # Add Back Door Face ID Section
        backdoor_frame = QFrame()
        backdoor_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        backdoor_layout = QVBoxLayout()
        backdoor_frame.setLayout(backdoor_layout)

        backdoor_icon_label = QLabel()
        backdoor_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\FaceID.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if backdoor_pixmap.isNull():
            print("Error: Face ID image not found.")
            backdoor_icon_label.setText("No Image")
        else:
            backdoor_icon_label.setPixmap(backdoor_pixmap)
        backdoor_icon_label.setAlignment(Qt.AlignCenter)
        backdoor_layout.addWidget(backdoor_icon_label)

        backdoor_name_label = QLabel("Open Back Door")
        backdoor_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        backdoor_name_label.setAlignment(Qt.AlignCenter)
        backdoor_layout.addWidget(backdoor_name_label)

        # Add Back Door Face ID Button
        backdoor_button_layout = QHBoxLayout()
        backdoor_button_layout.addStretch()
        backdoor_button = QPushButton("Verify")
        backdoor_button.setStyleSheet("""
            QPushButton {
                background-color: #ff7f50;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5722;
            }
        """)
        backdoor_button.clicked.connect(self.handle_faceid_backdoor_button)
        backdoor_button_layout.addWidget(backdoor_button)
        backdoor_button_layout.addStretch()
        backdoor_layout.addLayout(backdoor_button_layout)

        # Add to grid layout - position in row 1 (second row)
        self.devices_layout.addWidget(backdoor_frame, 1, 1)  # Place in row 1, column 1
        self.device_frames["Back Door"] = backdoor_frame

        # Add Control Panel in the empty space (position 1,0)
        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        control_layout = QVBoxLayout()
        control_frame.setLayout(control_layout)
        
        # Add a title for this section
        control_label = QLabel("Garage Controls")
        control_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        control_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(control_label)
        
        # Add control buttons
        control_buttons_layout = QVBoxLayout()
        
        # Close Back Door button 
        close_backdoor_button_layout = QHBoxLayout()  # Changed from "Close Back Door" to match other buttons
        close_backdoor_button_layout.addStretch()
        close_backdoor_button = QPushButton("Close Back Door")
      
        close_backdoor_button.setStyleSheet("""
             QPushButton {
                background-color: #ff7f50;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5722;
            }
        """)
        close_backdoor_button.clicked.connect(self.handle_close_backdoor_button)
        control_buttons_layout.addWidget(close_backdoor_button)
        
        # You can add more control buttons here
        
        control_layout.addLayout(control_buttons_layout)
        
        # Add to grid layout at position (1,0)
        self.devices_layout.addWidget(control_frame, 1, 0)
        self.device_frames["Garage Controls"] = control_frame

        # Create a dedicated Close Back Door frame (alternative approach)
        close_backdoor_frame = QFrame()
        close_backdoor_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        close_backdoor_layout = QVBoxLayout()
        close_backdoor_frame.setLayout(close_backdoor_layout)

        # Add the same icon
        close_backdoor_icon_label = QLabel()
        close_backdoor_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\closedoor.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if not close_backdoor_pixmap.isNull():
            close_backdoor_icon_label.setPixmap(close_backdoor_pixmap)
        close_backdoor_icon_label.setAlignment(Qt.AlignCenter)
        close_backdoor_layout.addWidget(close_backdoor_icon_label)

        # Add Title
        close_backdoor_name_label = QLabel("Close Back Door")
        close_backdoor_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        close_backdoor_name_label.setAlignment(Qt.AlignCenter)
        close_backdoor_layout.addWidget(close_backdoor_name_label)

        # Add button with styling
        close_door_button_layout = QHBoxLayout()
        close_door_button_layout.addStretch()
        close_backdoor_button = QPushButton("Close")
        close_backdoor_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e64a19;
            }
        """)
        close_backdoor_button.clicked.connect(self.handle_close_backdoor_button)
        close_door_button_layout.addWidget(close_backdoor_button)
        close_door_button_layout.addStretch()
        close_backdoor_layout.addLayout(close_door_button_layout)

        # Replace entire control frame with this one
        self.devices_layout.addWidget(close_backdoor_frame, 1, 0)
        self.device_frames["Close Back Door"] = close_backdoor_frame

    def show_living_room_functionalities(self):
        """Display functionalities for the Living Room."""
        # Clear existing devices first
        while self.devices_layout.count():
            child = self.devices_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.device_frames.clear()  # Clear the device_frames dictionary

        # Recreate Air Conditioner
        aircon_frame = QFrame()
        aircon_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        aircon_layout = QVBoxLayout()
        aircon_frame.setLayout(aircon_layout)

        aircon_icon_label = QLabel()
        aircon_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\airconditioner.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        aircon_icon_label.setPixmap(aircon_pixmap)
        aircon_icon_label.setAlignment(Qt.AlignCenter)
        aircon_layout.addWidget(aircon_icon_label)

        aircon_name_label = QLabel("Air Conditioner")
        aircon_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        aircon_name_label.setAlignment(Qt.AlignCenter)
        aircon_layout.addWidget(aircon_name_label)

        aircon_toggle_layout = QHBoxLayout()
        aircon_toggle_layout.addStretch()
        aircon_toggle = AnimatedToggle()
        aircon_toggle_layout.addWidget(aircon_toggle)
        aircon_toggle_layout.addStretch()
        aircon_layout.addLayout(aircon_toggle_layout)

        aircon_toggle.stateChanged.connect(self.handle_living_room_aircon_toggle)

        self.devices_layout.addWidget(aircon_frame, 0, 0)
        self.device_frames["Air Conditioner"] = aircon_frame

        # Recreate Bulb Lamp
        bulb_frame = QFrame()
        bulb_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        bulb_layout = QVBoxLayout()
        bulb_frame.setLayout(bulb_layout)

        bulb_icon_label = QLabel()
        bulb_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\light.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        bulb_icon_label.setPixmap(bulb_pixmap)
        bulb_icon_label.setAlignment(Qt.AlignCenter)
        bulb_layout.addWidget(bulb_icon_label)

        bulb_name_label = QLabel("Bulb Lamp")
        bulb_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        bulb_name_label.setAlignment(Qt.AlignCenter)
        bulb_layout.addWidget(bulb_name_label)

        bulb_toggle_layout = QHBoxLayout()
        bulb_toggle_layout.addStretch()
        bulb_toggle = AnimatedToggle()
        bulb_toggle_layout.addWidget(bulb_toggle)
        bulb_toggle_layout.addStretch()
        bulb_layout.addLayout(bulb_toggle_layout)

        bulb_toggle.stateChanged.connect(self.handle_living_room_bulb_toggle)

        self.devices_layout.addWidget(bulb_frame, 0, 1)
        self.device_frames["Bulb Lamp"] = bulb_frame

        # Recreate Gate 1
        gate1_frame = QFrame()
        gate1_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        gate1_layout = QVBoxLayout()
        gate1_frame.setLayout(gate1_layout)

        gate1_icon_label = QLabel()
        gate1_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\gate.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        gate1_icon_label.setPixmap(gate1_pixmap)
        gate1_icon_label.setAlignment(Qt.AlignCenter)
        gate1_layout.addWidget(gate1_icon_label)

        gate1_name_label = QLabel("Gate")
        gate1_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        gate1_name_label.setAlignment(Qt.AlignCenter)
        gate1_layout.addWidget(gate1_name_label)  # Correct - adds the name label

        # Add Gate 1 Toggle Button
        gate1_toggle_layout = QHBoxLayout()
        gate1_toggle_layout.addStretch()
        gate1_toggle = AnimatedToggle()
        gate1_toggle.setFixedSize(50, 25)
        gate1_toggle.stateChanged.connect(lambda state: self.handle_gate_toggle(state, "Gate"))
        gate1_toggle_layout.addWidget(gate1_toggle)
        gate1_toggle_layout.addStretch()
        gate1_layout.addLayout(gate1_toggle_layout)

        self.devices_layout.addWidget(gate1_frame, 1, 0)
        self.device_frames["Gate 1"] = gate1_frame

        # Recreate Face ID (replacing Gate 2)
        faceid_frame = QFrame()
        faceid_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        faceid_layout = QVBoxLayout()
        faceid_frame.setLayout(faceid_layout)

        faceid_icon_label = QLabel()
        faceid_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\FaceID.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if faceid_pixmap.isNull():
            print("Error: Face ID image not found.")
            faceid_icon_label.setText("No Image")
        else:
            faceid_icon_label.setPixmap(faceid_pixmap)
        faceid_icon_label.setAlignment(Qt.AlignCenter)
        faceid_layout.addWidget(faceid_icon_label)

        faceid_name_label = QLabel("Open Main Door")
        faceid_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        faceid_name_label.setAlignment(Qt.AlignCenter)
        faceid_layout.addWidget(faceid_name_label)

        # Add Face ID Button (not toggle)
        faceid_button_layout = QHBoxLayout()
        faceid_button_layout.addStretch()
        faceid_button = QPushButton("Verify")
        faceid_button.setStyleSheet("""
            QPushButton {
                background-color: #ff7f50;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5722;
            }
        """)
        faceid_button.clicked.connect(self.handle_faceid_button)
        faceid_button_layout.addWidget(faceid_button)

        # Add a small spacing between buttons
        faceid_button_layout.addSpacing(10)

        # Add Close Main Door button
        close_maindoor_button = QPushButton("Close")
        close_maindoor_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e64a19;
            }
        """)
        close_maindoor_button.clicked.connect(self.handle_close_maindoor_button)
        faceid_button_layout.addWidget(close_maindoor_button)

        faceid_button_layout.addStretch()
        faceid_layout.addLayout(faceid_button_layout)

        self.devices_layout.addWidget(faceid_frame, 1, 1)
        self.device_frames["Face ID"] = faceid_frame

    def show_kitchen_functionalities(self):
        """Display functionalities for the Kitchen."""
        print("Kitchen functionalities displayed.")
        
        # Clear existing devices first
        while self.devices_layout.count():
            child = self.devices_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.device_frames.clear()  # Clear the device_frames dictionary

        # Create Air Conditioner Frame
        aircon_frame = QFrame()
        aircon_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        aircon_layout = QVBoxLayout()
        aircon_frame.setLayout(aircon_layout)

        aircon_icon_label = QLabel()
        aircon_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\airconditioner.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        aircon_icon_label.setPixmap(aircon_pixmap)
        aircon_icon_label.setAlignment(Qt.AlignCenter)
        aircon_layout.addWidget(aircon_icon_label)

        aircon_name_label = QLabel("Air Conditioner")
        aircon_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        aircon_name_label.setAlignment(Qt.AlignCenter)
        aircon_layout.addWidget(aircon_name_label)

        aircon_toggle_layout = QHBoxLayout()
        aircon_toggle_layout.addStretch()
        aircon_toggle = AnimatedToggle()
        aircon_toggle_layout.addWidget(aircon_toggle)
        aircon_toggle_layout.addStretch()
        aircon_layout.addLayout(aircon_toggle_layout)

        aircon_toggle.stateChanged.connect(self.handle_kitchen_aircon_toggle)

        self.devices_layout.addWidget(aircon_frame, 0, 0)
        self.device_frames["Air Conditioner"] = aircon_frame

        # Create Bulb Lamp Frame
        bulb_frame = QFrame()
        bulb_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        bulb_layout = QVBoxLayout()
        bulb_frame.setLayout(bulb_layout)

        bulb_icon_label = QLabel()
        bulb_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\light.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        bulb_icon_label.setPixmap(bulb_pixmap)
        bulb_icon_label.setAlignment(Qt.AlignCenter)
        bulb_layout.addWidget(bulb_icon_label)

        bulb_name_label = QLabel("Bulb Lamp")
        bulb_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        bulb_name_label.setAlignment(Qt.AlignCenter)
        bulb_layout.addWidget(bulb_name_label)

        bulb_toggle_layout = QHBoxLayout()
        bulb_toggle_layout.addStretch()
        bulb_toggle = AnimatedToggle()
        bulb_toggle_layout.addWidget(bulb_toggle)
        bulb_toggle_layout.addStretch()
        bulb_layout.addLayout(bulb_toggle_layout)

        bulb_toggle.stateChanged.connect(self.handle_kitchen_bulb_toggle)

        self.devices_layout.addWidget(bulb_frame, 0, 1)
        self.device_frames["Bulb Lamp"] = bulb_frame

    def show_bedroom_functionalities(self):
        """Display functionalities for the Bedroom."""
        print("Bedroom functionalities displayed.")
        
        # Clear existing devices first
        while self.devices_layout.count():
            child = self.devices_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.device_frames.clear()  # Clear the device_frames dictionary

        # Create Air Conditioner Frame
        aircon_frame = QFrame()
        aircon_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        aircon_layout = QVBoxLayout()
        aircon_frame.setLayout(aircon_layout)

        aircon_icon_label = QLabel()
        aircon_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\airconditioner.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        aircon_icon_label.setPixmap(aircon_pixmap)
        aircon_icon_label.setAlignment(Qt.AlignCenter)
        aircon_layout.addWidget(aircon_icon_label)

        aircon_name_label = QLabel("Air Conditioner")
        aircon_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        aircon_name_label.setAlignment(Qt.AlignCenter)
        aircon_layout.addWidget(aircon_name_label)

        aircon_toggle_layout = QHBoxLayout()
        aircon_toggle_layout.addStretch()
        aircon_toggle = AnimatedToggle()
        aircon_toggle_layout.addWidget(aircon_toggle)
        aircon_toggle_layout.addStretch()
        aircon_layout.addLayout(aircon_toggle_layout)

        aircon_toggle.stateChanged.connect(self.handle_bedroom_aircon_toggle)

        self.devices_layout.addWidget(aircon_frame, 0, 0)
        self.device_frames["Air Conditioner"] = aircon_frame

        # Create Bulb Lamp Frame
        bulb_frame = QFrame()
        bulb_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        bulb_layout = QVBoxLayout()
        bulb_frame.setLayout(bulb_layout)

        bulb_icon_label = QLabel()
        bulb_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\light.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        bulb_icon_label.setPixmap(bulb_pixmap)
        bulb_icon_label.setAlignment(Qt.AlignCenter)
        bulb_layout.addWidget(bulb_icon_label)

        bulb_name_label = QLabel("Bulb Lamp")
        bulb_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        bulb_name_label.setAlignment(Qt.AlignCenter)
        bulb_layout.addWidget(bulb_name_label)

        bulb_toggle_layout = QHBoxLayout()
        bulb_toggle_layout.addStretch()
        bulb_toggle = AnimatedToggle()
        bulb_toggle_layout.addWidget(bulb_toggle)
        bulb_toggle_layout.addStretch()
        bulb_layout.addLayout(bulb_toggle_layout)

        bulb_toggle.stateChanged.connect(self.handle_bedroom_bulb_toggle)

        self.devices_layout.addWidget(bulb_frame, 0, 1)
        self.device_frames["Bulb Lamp"] = bulb_frame

    def show_gym_functionalities(self):
        """Display functionalities for the Gym."""
        print("Gym functionalities displayed.")
        
        # Clear existing devices first
        while self.devices_layout.count():
            child = self.devices_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.device_frames.clear()  # Clear the device_frames dictionary

        # Create Air Conditioner Frame
        aircon_frame = QFrame()
        aircon_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        aircon_layout = QVBoxLayout()
        aircon_frame.setLayout(aircon_layout)

        aircon_icon_label = QLabel()
        aircon_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\airconditioner.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        aircon_icon_label.setPixmap(aircon_pixmap)
        aircon_icon_label.setAlignment(Qt.AlignCenter)
        aircon_layout.addWidget(aircon_icon_label)

        aircon_name_label = QLabel("Air Conditioner")
        aircon_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        aircon_name_label.setAlignment(Qt.AlignCenter)
        aircon_layout.addWidget(aircon_name_label)

        aircon_toggle_layout = QHBoxLayout()
        aircon_toggle_layout.addStretch()
        aircon_toggle = AnimatedToggle()
        aircon_toggle_layout.addWidget(aircon_toggle)
        aircon_toggle_layout.addStretch()
        aircon_layout.addLayout(aircon_toggle_layout)

        aircon_toggle.stateChanged.connect(self.handle_gym_aircon_toggle)

        self.devices_layout.addWidget(aircon_frame, 0, 0)
        self.device_frames["Air Conditioner"] = aircon_frame

        # Create Bulb Lamp Frame
        bulb_frame = QFrame()
        bulb_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        bulb_layout = QVBoxLayout()
        bulb_frame.setLayout(bulb_layout)

        bulb_icon_label = QLabel()
        bulb_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\light.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        bulb_icon_label.setPixmap(bulb_pixmap)
        bulb_icon_label.setAlignment(Qt.AlignCenter)
        bulb_layout.addWidget(bulb_icon_label)

        bulb_name_label = QLabel("Bulb Lamp")
        bulb_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        bulb_name_label.setAlignment(Qt.AlignCenter)
        bulb_layout.addWidget(bulb_name_label)

        bulb_toggle_layout = QHBoxLayout()
        bulb_toggle_layout.addStretch()
        bulb_toggle = AnimatedToggle()
        bulb_toggle_layout.addWidget(bulb_toggle)
        bulb_toggle_layout.addStretch()
        bulb_layout.addLayout(bulb_toggle_layout)

        bulb_toggle.stateChanged.connect(self.handle_gym_bulb_toggle)

        self.devices_layout.addWidget(bulb_frame, 0, 1)
        self.device_frames["Bulb Lamp"] = bulb_frame

    def handle_gate_toggle(self, state, gate_name="Gate"):
        """Handle the toggle state of the Gate."""
        if state:
            print(f"{gate_name} is now OPEN.")
            # Add code to open the gate (e.g., send a signal to hardware)
            if self.serial_port:
                try:
                    self.serial_port.write(b"OPEN_MAIN_GATE\n")
                    print("[SERIAL] Sent: OPEN_MAIN_GATE")
                except Exception as e:
                    print(f"Error sending gate command: {e}")
            
        else:
            print(f"{gate_name} is now CLOSED.")
            # Add code to close the gate (e.g., send a signal to hardware)
            if self.serial_port:
                try:
                    self.serial_port.write(b"CLOSE_MAIN_GATE\n")
                    print("[SERIAL] Sent: CLOSE_MAIN_GATE")
                except Exception as e:
                    print(f"Error sending gate command: {e}")

    def handle_faceid_button(self):
        """Handle the Face ID button click."""
        print("Face ID scan initiated.")
        
        # Close the serial connection first
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
        
        try:
            subprocess.run(["python", r"A:\College stuff\DATA AQ\face-recognition-app\src\main.py"])
        except Exception as e:
            print(f"Error running face recognition script: {e}")
        
        # Reopen the serial connection after main.py completes
        for attempt in range(3):  # Try 3 times
            try:
                self.serial_port = serial.Serial('COM6', 9600, timeout=1)
                print("Serial port reopened successfully")
                break
            except serial.SerialException:
                print(f"Error: Could not reopen serial port (Attempt {attempt+1}/3)")
                time.sleep(1)  # Wait a bit before retrying
                
        if self.serial_port is None:
            print("Failed to reopen serial port after multiple attempts")

    def handle_kitchen_aircon_toggle(self, state):
        """Handle the toggle state of the Kitchen Air Conditioner."""
        if state:
            print("Kitchen Air Conditioner is now ON.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"AIRCON_ON\n")
                    print("[SERIAL] Sent: KITCHEN_AIRCON_ON")
                except Exception as e:
                    print(f"Error sending kitchen aircon command: {e}")
        else:
            print("Kitchen Air Conditioner is now OFF.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"AIRCON_OFF\n")
                    print("[SERIAL] Sent: KITCHEN_AIRCON_OFF")
                except Exception as e:
                    print(f"Error sending kitchen aircon command: {e}")

    def handle_kitchen_bulb_toggle(self, state):
        """Handle the toggle state of the Kitchen Bulb Lamp."""
        if state:
            print("Kitchen Bulb Lamp is now ON.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"KITCHEN_BULB_ON\n")
                    print("[SERIAL] Sent: KITCHEN_BULB_ON")
                except Exception as e:
                    print(f"Error sending kitchen bulb command: {e}")
        else:
            print("Kitchen Bulb Lamp is now OFF.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"KITCHEN_BULB_OFF\n")
                    print("[SERIAL] Sent: KITCHEN_BULB_OFF")
                except Exception as e:
                    print(f"Error sending kitchen bulb command: {e}")

    def handle_bedroom_aircon_toggle(self, state):
        """Handle the toggle state of the Bedroom Air Conditioner."""
        if state:
            print("Bedroom Air Conditioner is now ON.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"AIRCON_ON\n")
                    print("[SERIAL] Sent: BEDROOM_AIRCON_ON")
                except Exception as e:
                    print(f"Error sending bedroom aircon command: {e}")
        else:
            print("Bedroom Air Conditioner is now OFF.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"AIRCON_OFF\n")
                    print("[SERIAL] Sent: BEDROOM_AIRCON_OFF")
                except Exception as e:
                    print(f"Error sending bedroom aircon command: {e}")

    def handle_bedroom_bulb_toggle(self, state):
        """Handle the toggle state of the Bedroom Bulb Lamp."""
        if state:
            print("Bedroom Bulb Lamp is now ON.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"BEDROOM_BULB_ON\n")
                    print("[SERIAL] Sent: BEDROOM_BULB_ON")
                except Exception as e:
                    print(f"Error sending bedroom bulb command: {e}")
        else:
            print("Bedroom Bulb Lamp is now OFF.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"BEDROOM_BULB_OFF\n")
                    print("[SERIAL] Sent: BEDROOM_BULB_OFF")
                except Exception as e:
                    print(f"Error sending bedroom bulb command: {e}")

    def handle_gym_aircon_toggle(self, state):
        """Handle the toggle state of the Gym Air Conditioner."""
        if state:
            print("Gym Air Conditioner is now ON.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"AIRCON_ON\n")
                    print("[SERIAL] Sent: GYM_AIRCON_ON")
                except Exception as e:
                    print(f"Error sending gym aircon command: {e}")
        else:
            print("Gym Air Conditioner is now OFF.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"AIRCON_OFF\n")
                    print("[SERIAL] Sent: GYM_AIRCON_OFF")
                except Exception as e:
                    print(f"Error sending gym aircon command: {e}")

    def handle_gym_bulb_toggle(self, state):
        """Handle the toggle state of the Gym Bulb Lamp."""
        if state:
            print("Gym Bulb Lamp is now ON.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"GYM_BULB_ON\n")
                    print("[SERIAL] Sent: GYM_BULB_ON")
                except Exception as e:
                    print(f"Error sending gym bulb command: {e}")
        else:
            print("Gym Bulb Lamp is now OFF.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"GYM_BULB_OFF\n")
                    print("[SERIAL] Sent: GYM_BULB_OFF")
                except Exception as e:
                    print(f"Error sending gym bulb command: {e}")

    def handle_faceid_backdoor_button(self):
        """Handle the Face ID Back Door button click."""
        print("Face ID scan for back door initiated.")
        
        # Close the serial connection first
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
        
        try:
            # Run face recognition with a parameter to indicate back door
            subprocess.run(["python", r"A:\College stuff\DATA AQ\face-recognition-app\src\main.py", "--door=back"])
        except Exception as e:
            print(f"Error running face recognition script: {e}")
        
        # Reopen the serial connection after main.py completes
        for attempt in range(3):  # Try 3 times
            try:
                self.serial_port = serial.Serial('COM6', 9600, timeout=1)
                print("Serial port reopened successfully")
                break
            except serial.SerialException:
                print(f"Error: Could not reopen serial port (Attempt {attempt+1}/3)")
                time.sleep(1)  # Wait a bit before retrying
                
        if self.serial_port is None:
            print("Failed to reopen serial port after multiple attempts")

    def handle_close_backdoor_button(self):
        """Handle the Close Back Door button click."""
        print("Closing back door...")
        if self.serial_port:
            try:
                self.serial_port.write(b"CLOSE_BACK_DOOR\n")
                print("[SERIAL] Sent: CLOSE_BACK_DOOR")
            except Exception as e:
                print(f"Error sending close back door command: {e}")

    def handle_close_maindoor_button(self):
        """Handle the Close Main Door button click."""
        print("Closing main door...")
        if self.serial_port:
            try:
                self.serial_port.write(b"CLOSE_MAIN_DOOR\n")
                print("[SERIAL] Sent: CLOSE_MAIN_DOOR")
            except Exception as e:
                print(f"Error sending close main door command: {e}")

    def handle_living_room_aircon_toggle(self, state):
        """Handle the toggle state of the Living Room Air Conditioner."""
        if state:
            print("Living Room Air Conditioner is now ON.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"AIRCON_ON\n")
                    print("[SERIAL] Sent: LIVING_ROOM_AIRCON_ON")
                except Exception as e:
                    print(f"Error sending living room aircon command: {e}")
        else:
            print("Living Room Air Conditioner is now OFF.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"AIRCON_OFF\n")
                    print("[SERIAL] Sent: LIVING_ROOM_AIRCON_OFF")
                except Exception as e:
                    print(f"Error sending living room aircon command: {e}")

    def handle_living_room_bulb_toggle(self, state):
        """Handle the toggle state of the Living Room Bulb Lamp."""
        if state:
            print("Living Room Bulb Lamp is now ON.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"LIVING_ROOM_BULB_ON\n")
                    print("[SERIAL] Sent: LIVING_ROOM_BULB_ON")
                except Exception as e:
                    print(f"Error sending living room bulb command: {e}")
        else:
            print("Living Room Bulb Lamp is now OFF.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"LIVING_ROOM_BULB_OFF\n")
                    print("[SERIAL] Sent: LIVING_ROOM_BULB_OFF")
                except Exception as e:
                    print(f"Error sending living room bulb command: {e}")

    def handle_garage_light_toggle(self, state):
        """Handle the toggle state of the Garage Light."""
        if state:
            print("Garage Light is now ON.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"GARAGE_LIGHT_ON\n")
                    print("[SERIAL] Sent: GARAGE_LIGHT_ON")
                except Exception as e:
                    print(f"Error sending garage light command: {e}")
        else:
            print("Garage Light is now OFF.")
            if self.serial_port:
                try:
                    self.serial_port.write(b"GARAGE_LIGHT_OFF\n")
                    print("[SERIAL] Sent: GARAGE_LIGHT_OFF")
                except Exception as e:
                    print(f"Error sending garage light command: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartHomeApp()
    window.show()
    sys.exit(app.exec_())