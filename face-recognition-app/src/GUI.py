import sys
import serial  # For serial communication
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QGridLayout, QFrame, QCheckBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer

# Add this import for the AnimatedToggle
from animated_toggle import AnimatedToggle  # Save the AnimatedToggle class in a file named animated_toggle.py


class SmartHomeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Home Control Panel")
        self.setGeometry(100, 100, 400, 800)

        # Initialize Serial Communication
        try:
            self.serial_port = serial.Serial('COM3', 9600, timeout=1)  # Replace 'COM3' with your Arduino's port
        except serial.SerialException:
            print("Error: Could not open serial port.")
            self.serial_port = None

        # Main Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main Layout
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Header Section
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #ff7f50; border-radius: 10px;")
        header_layout = QHBoxLayout()
        header_frame.setLayout(header_layout)

        profile_pic = QLabel()
        profile_pixmap = QPixmap(r"A:\College stuff\DATA AQ\Nour1.jpg")
        if profile_pixmap.isNull():
            print("Error: profile.jpg not found.")
        profile_pixmap = profile_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        profile_pic.setPixmap(profile_pixmap)
        profile_pic.setStyleSheet("border-radius: 25px;")
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
            {"name": "Living Room", "icon": r"A:\College stuff\DATA AQ\GUI\icons\living_room.jpg"},
            {"name": "Kitchen", "icon": r"A:\College stuff\DATA AQ\GUI\icons\kitchen.jpg"},
            {"name": "Garage", "icon": r"A:\College stuff\DATA AQ\GUI\icons\garage.jpg"},
            {"name": "Bedroom", "icon": r"A:\College stuff\DATA AQ\GUI\icons\bedroom.jpg"}
        ]

        for i, room in enumerate(room_buttons):
            room_button = QPushButton(room["name"])
            room_button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {'#ff7f50' if i == 0 else 'white'};
                    color: {'white' if i == 0 else 'black'};
                    border: 1px solid #ff7f50;
                    border-radius: 10px;
                    padding: 10px;
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
            rooms_layout.addWidget(room_button)

        main_layout.addLayout(rooms_layout)

        # Devices Section
        devices_label = QLabel("Devices")
        devices_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px 0;")
        main_layout.addWidget(devices_label)

        devices_layout = QGridLayout()
        devices = [
            {"name": "Air Conditioner", "icon": r"A:\College stuff\DATA AQ\GUI\icons\airconditioner.jpg"},
            {"name": "Bulb Lamp", "icon": r"A:\College stuff\DATA AQ\GUI\icons\light.jpg"},
            {"name": "Smart TV", "icon": r"A:\College stuff\DATA AQ\GUI\icons\tv_icon.jpg"},
            {"name": "WiFi Router", "icon": r"A:\College stuff\DATA AQ\GUI\icons\wifi_icon.jpg"}
        ]

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
            name_label.setStyleSheet("font-size: 12px; font-weight: bold; text-align: center;")
            name_label.setAlignment(Qt.AlignCenter)
            device_layout.addWidget(name_label)

            # Add the animated toggle button
            toggle_button_layout = QHBoxLayout()
            toggle_button_layout.addStretch()
            toggle_button = AnimatedToggle()
            toggle_button_layout.addWidget(toggle_button)
            toggle_button_layout.addStretch()
            device_layout.addLayout(toggle_button_layout)

            devices_layout.addWidget(device_frame, i // 2, i % 2)

        main_layout.addLayout(devices_layout)

        # Footer Section
        footer_layout = QHBoxLayout()
        home_button = QPushButton("Home")
        home_button.setStyleSheet("background-color: #ff7f50; color: white; border-radius: 10px; padding: 10px;")
        footer_layout.addWidget(home_button)

        settings_button = QPushButton("Settings")
        settings_button.setStyleSheet("background-color: #ff7f50; color: white; border-radius: 10px; padding: 10px;")
        footer_layout.addWidget(settings_button)

        main_layout.addLayout(footer_layout)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartHomeApp()
    window.show()
    sys.exit(app.exec_())