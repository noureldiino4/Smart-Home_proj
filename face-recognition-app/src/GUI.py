import sys
import serial  # For serial communication
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
            self.serial_port = serial.Serial('COM3', 9600, timeout=1)  # Replace 'COM3' with your Arduino's port
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
            {"name": "Bedroom", "icon": r"A:\College stuff\DATA AQ\GUI\icons\bedroom.jpg"}
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

        # Add Gate Section
        gate_frame = QFrame()
        gate_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        gate_layout = QVBoxLayout()
        gate_frame.setLayout(gate_layout)

        # Add Gate Icon
        gate_icon_label = QLabel()
        gate_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\gate.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if gate_pixmap.isNull():
            print("Error: gate.jpg not found.")
            gate_icon_label.setText("No Image")
        else:
            gate_icon_label.setPixmap(gate_pixmap)
        gate_icon_label.setAlignment(Qt.AlignCenter)
        gate_layout.addWidget(gate_icon_label)

        # Add Gate Label
        gate_name_label = QLabel("Gate")
        gate_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        gate_name_label.setAlignment(Qt.AlignCenter)
        gate_layout.addWidget(gate_name_label)

        # Add Gate Toggle Button
        gate_toggle_layout = QHBoxLayout()
        gate_toggle_layout.addStretch()
        gate_toggle = AnimatedToggle()
        gate_toggle.setFixedSize(50, 25)  # Match the size of other toggles
        gate_toggle.stateChanged.connect(self.handle_gate_toggle)  # Connect to a handler
        gate_toggle_layout.addWidget(gate_toggle)
        gate_toggle_layout.addStretch()
        gate_layout.addLayout(gate_toggle_layout)

        # Add Gate Frame to Devices Layout
        self.devices_layout.addWidget(gate_frame, 1, 0, 1, 2)  # Add Gate to the layout spanning 2 columns
        self.device_frames["Gate"] = gate_frame

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

    def show_garage_functionalities(self):
        """Display functionalities for the Garage."""
        devices_layout = self.devices_layout

        aircon_frame = self.device_frames.get("Air Conditioner")
        if aircon_frame:
            # Create Garage Door Frame
            garage_door_frame = QFrame()
            garage_door_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
            garage_door_layout = QVBoxLayout()
            garage_door_frame.setLayout(garage_door_layout)

            # Add Garage Door Photo
            garage_door_icon_label = QLabel()
            garage_door_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\garage.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if garage_door_pixmap.isNull():
                print("Error: garage-door.jpg not found.")
                garage_door_icon_label.setText("No Image")
            else:
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
            garage_door_toggle.setFixedSize(50, 25)  # Match the size of the Bulb Lamp toggle
            garage_door_toggle_layout.addWidget(garage_door_toggle)
            garage_door_toggle_layout.addStretch()
            garage_door_layout.addLayout(garage_door_toggle_layout)

            # Replace frame in the layout
            index = devices_layout.indexOf(aircon_frame)
            row = index // 2  # Calculate the row
            col = index % 2   # Calculate the column
            devices_layout.removeWidget(aircon_frame)
            aircon_frame.deleteLater()

            devices_layout.addWidget(garage_door_frame, row, col)  # Use row and column

            # Update the dictionary
            self.device_frames["Garage Door"] = garage_door_frame
            del self.device_frames["Air Conditioner"]

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

        self.devices_layout.addWidget(bulb_frame, 0, 1)
        self.device_frames["Bulb Lamp"] = bulb_frame

        # Recreate Gate
        gate_frame = QFrame()
        gate_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 10px;")
        gate_layout = QVBoxLayout()
        gate_frame.setLayout(gate_layout)

        gate_icon_label = QLabel()
        gate_pixmap = QPixmap(r"A:\College stuff\DATA AQ\GUI\icons\gate.jpg").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        gate_icon_label.setPixmap(gate_pixmap)
        gate_icon_label.setAlignment(Qt.AlignCenter)
        gate_layout.addWidget(gate_icon_label)

        gate_name_label = QLabel("Gate")
        gate_name_label.setStyleSheet("font-size: 18px; font-weight: bold; text-align: center;")
        gate_name_label.setAlignment(Qt.AlignCenter)
        gate_layout.addWidget(gate_name_label)

        # Add Gate Toggle Button
        gate_toggle_layout = QHBoxLayout()
        gate_toggle_layout.addStretch()
        gate_toggle = AnimatedToggle()
        gate_toggle.setFixedSize(50, 25)  # Match the size of other toggles
        gate_toggle.stateChanged.connect(self.handle_gate_toggle)  # Connect to a handler
        gate_toggle_layout.addWidget(gate_toggle)
        gate_toggle_layout.addStretch()
        gate_layout.addLayout(gate_toggle_layout)

        self.devices_layout.addWidget(gate_frame, 1, 0, 1, 2)
        self.device_frames["Gate"] = gate_frame

    def show_kitchen_functionalities(self):
        """Display functionalities for the Kitchen."""
        print("Kitchen functionalities displayed.")
        # Add code here to update the UI for Kitchen-specific functionalities.

    def show_bedroom_functionalities(self):
        """Display functionalities for the Bedroom."""
        print("Bedroom functionalities displayed.")
        # Add code here to update the UI for Bedroom-specific functionalities.

    def handle_gate_toggle(self, state):
        """Handle the toggle state of the Gate."""
        if state:
            print("Gate is now OPEN.")
            # Add code to open the gate (e.g., send a signal to hardware)
        else:
            print("Gate is now CLOSED.")
            # Add code to close the gate (e.g., send a signal to hardware)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartHomeApp()
    window.show()
    sys.exit(app.exec_())