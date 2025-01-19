import sys
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QGroupBox, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, 
    QGridLayout, QFrame, QFileDialog)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPixmap
import os
from datetime import datetime, timedelta
import serial

class CanSatGroundControl(QMainWindow):
    def __init__(self):
        
        super().__init__()
        self.data = None
        self.current_index = 0
        self.mission_start_time = None  # To keep track of mission start time
        self.elapsed_time = timedelta()  # To store elapsed time for the mission
        self.initUI()
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second

    def initUI(self):
        self.setWindowTitle("CanSat2024")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Top bar
        top_bar = QHBoxLayout()
        
        # Logo and team info container
        logo_container = QHBoxLayout()
        
        # Logo
        logo_label = QLabel("TARSR")  # Text instead of image
        logo_label.setFont(QFont('Arial', 20, QFont.Bold))
        logo_label.setFixedSize(120, 50)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Team info labels
        self.team_id_label = QLabel("2000")
        self.team_id_label.setFont(QFont('Arial', 12))
        
        logo_container.addWidget(logo_label)
        # logo_container.addWidget(QLabel("AEROSPACE"))  # Add AEROSPACE text
        logo_container.addWidget(self.team_id_label)
        logo_container.addStretch()
        
        top_bar.addLayout(logo_container)
        
        # Connection controls
        connection_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.addItem("ttyACM0")
        refresh_btn = QPushButton("Refresh")
        connect_btn = QPushButton("Connect")
        disconnect_btn = QPushButton("Disconnect")
        
        refresh_btn.clicked.connect(self.load_csv_file)
        
        connection_layout.addWidget(self.port_combo)
        connection_layout.addWidget(refresh_btn)
        connection_layout.addWidget(connect_btn)
        connection_layout.addWidget(disconnect_btn)
        top_bar.addLayout(connection_layout)
        
        main_layout.addLayout(top_bar)
        
        # Tab bar
        tab_layout = QHBoxLayout()
        tabs = ["Logs", "Commands", "Charts", "About", "Simulation"]
        for tab in tabs:
            btn = QPushButton(tab)
            tab_layout.addWidget(btn)
        main_layout.addLayout(tab_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left panel - Telemetry data
        telemetry_group = QGroupBox()
        telemetry_layout = QGridLayout()
        
        # Define telemetry fields
        telemetry_fields = [
            ("Team ID:", "2044"),
            ("Mission Time:", "00:00:00"),
            ("Packet Count:", "32"),
            ("Mode:", "S"),
            ("State:", "S"),
            ("Altitude:", "32"),
            ("Air Speed:", "34"),
            ("Heatshield deployed:", "N"),
            ("Parachute deployed:", "N"),
            ("Temperature:", "20"),
            ("Voltage:", "3"),
            ("Pressure:", "-22"),
            ("GPS Time:", "12:00:0"),
            ("GPS Altitude:", "5"),
            ("GPS Latitude:", "55"),
            ("GPS Longitude:", "23"),
            ("GPS Sats:", "5"),
            ("Tilt X:", "5"),
            ("Tilt Y:", "5"),
            ("Rotation Z:", "15"),
            ("CMD Echo:", "NO_CMD"),
            ("Camera 1 State:", "OK"),
            ("Camera 2 State:", "OK")
        ]
        
        self.telemetry_labels = {}
        for i, (label, initial_value) in enumerate(telemetry_fields):
            telemetry_layout.addWidget(QLabel(label), i, 0)
            self.telemetry_labels[label] = QLabel(initial_value)
            telemetry_layout.addWidget(self.telemetry_labels[label], i, 1)
        
        telemetry_group.setLayout(telemetry_layout)
        content_layout.addWidget(telemetry_group)
        
        # Right panel - Graphs
        graphs_layout = QGridLayout()
        
        # Create graphs
        graph_configs = [
            ("Pressure", "Pa"),
            ("Altitude", "m"),
            ("Tilt X", "deg"),
            ("Temperature", "°C"),
            ("Air speed", "m/s"),
            ("Tilt Y", "deg")
        ]
        
        self.plots = {}
        for i, (title, unit) in enumerate(graph_configs):
            plot = pg.PlotWidget()
            plot.setBackground('w')
            plot.showGrid(x=True, y=True)
            plot.setLabel('left', f'{title} ({unit})')
            plot.setLabel('bottom', 'Packet')
            plot.setTitle(title)
            
            self.plots[title] = {
                'widget': plot,
                'curve': plot.plot(pen=pg.mkPen(color='b', width=2))
            }
            
            graphs_layout.addWidget(plot, i//3, i%3)
        
        content_layout.addLayout(graphs_layout)
        
        # Set content layout stretch
        content_layout.setStretchFactor(telemetry_group, 1)
        content_layout.setStretchFactor(graphs_layout, 4)
        
        main_layout.addLayout(content_layout)
        
        # Bottom bar - Command input
        bottom_layout = QHBoxLayout()
        cmd_input = QLineEdit()
        cmd_input.setPlaceholderText("CMD,2044,")
        send_btn = QPushButton("SEND")
        log_level = QComboBox()
        log_level.addItem("ERROR (lowest)")
        
        bottom_layout.addWidget(cmd_input)
        bottom_layout.addWidget(send_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(QLabel("Log level:"))
        bottom_layout.addWidget(log_level)
        
        main_layout.addLayout(bottom_layout)
        
        self.setCentralWidget(central_widget)

    def load_csv_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            try:
                self.data = pd.read_csv(file_name)
                self.current_index = 0
                print("CSV file loaded successfully")
                self.start_mission_timer()  # Start the mission timer after loading the CSV
            except Exception as e:
                print(f"Error loading CSV file: {e}")

    def start_mission_timer(self):
        """Start the mission timer when the simulation starts."""
        self.mission_start_time = datetime.now()
        self.elapsed_time = timedelta()  # Reset the elapsed time
        self.timer.timeout.connect(self.update_mission_time)  # Connect to mission time update
        print("Mission timer started.")

    def update_mission_time(self):
        """Update the mission time displayed on the GUI."""
        if self.mission_start_time:
            self.elapsed_time = datetime.now() - self.mission_start_time
            mission_time_str = str(self.elapsed_time).split('.')[0]  # Get HH:MM:SS
            self.telemetry_labels["Mission Time:"].setText(mission_time_str)

    def update_data(self):
        if self.data is not None and self.current_index < len(self.data):
            row = self.data.iloc[self.current_index]
            
            # Update telemetry labels
            mapping = {
                "Team ID:": "TEAM_ID",
                "Mission Time:": self.get_mission_time(),
                "Packet Count:": "PACKET_COUNT",
                "Mode:": "MODE",
                "State:": "STATE",
                "Altitude:": "ALTITUDE",
                "Air Speed:": "AIR_SPEED",
                "Heatshield deployed:": "HS_DEPLOYED",
                "Parachute deployed:": "PC_DEPLOYED",
                "Temperature:": "TEMPERATURE",
                "Voltage:": "VOLTAGE",
                "Pressure:": "PRESSURE",
                "GPS Time:": "GPS_TIME",
                "GPS Altitude:": "GPS_ALTITUDE",
                "GPS Latitude:": "GPS_LATITUDE",
                "GPS Longitude:": "GPS_LONGITUDE",
                "GPS Sats:": "GPS_SATS",
                "Tilt X:": "TILT_X",
                "Tilt Y:": "TILT_Y",
                "Rotation Z:": "ROT_Z",
                "CMD Echo:": "CMD_ECHO"
            }
            
            for label, column in mapping.items():
                if label in self.telemetry_labels:
                    if column == "MISSION_TIME":
                        self.telemetry_labels[label].setText(self.get_mission_time())
                    elif column in row:
                        self.telemetry_labels[label].setText(str(row[column]))
            
            # Update graphs
            for title, plot_data in self.plots.items():
                column_mapping = {
                    "Pressure": "PRESSURE",
                    "Altitude": "ALTITUDE",
                    "Tilt X": "TILT_X",
                    "Temperature": "TEMPERATURE",
                    "Air speed": "AIR_SPEED",
                    "Tilt Y": "TILT_Y"
                }
                
                column = column_mapping.get(title)
                if column in self.data.columns:
                    y_data = self.data[column][:self.current_index + 1].tolist()
                    x_data = list(range(len(y_data)))
                    plot_data['curve'].setData(x_data, y_data)
            
            self.current_index += 1

    def get_mission_time(self):
        """Returns the formatted mission time."""
        return str(self.elapsed_time).split('.')[0]  # HH:MM:SS format

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_window = CanSatGroundControl()
    main_window.show()
    sys.exit(app.exec_())