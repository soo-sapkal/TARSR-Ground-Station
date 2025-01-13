import sys
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QGroupBox, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, 
    QGridLayout, QFrame)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPixmap
import os
from datetime import datetime
import serial

class CanSatGroundControl(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize serial connection
        self.serial_connection = None
        self.serial_data_buffer = []
        self.connect_to_serial()
        
        self.initUI()
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second

    def connect_to_serial(self):
        try:
            # Replace 'COM3' with the appropriate port for your system
            self.serial_connection = serial.Serial(port='COM3', baudrate=9600, timeout=1)
        except serial.SerialException as e:
            print(f"Error connecting to serial port: {e}")

    def initUI(self):
        self.setWindowTitle("Ground Control System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Top bar
        top_bar = QHBoxLayout()
        
        # Logo and team info container
        logo_container = QHBoxLayout()
        
        # Logo with empty image path
        logo_label = QLabel()
        logo_path = "logo.png"  # Just replace this path with your logo path
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(50, 50)
        logo_label.setStyleSheet("border: 1px solid #ccc;")  # Light border to show logo area when empty
        
        # Team name label
        team_label = QLabel("TEAM ANANTAM")
        team_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        logo_container.addWidget(logo_label)
        logo_container.addWidget(team_label)
        logo_container.addStretch()
        
        top_bar.addLayout(logo_container)
        
        # Connection controls
        connection_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.addItem("COM3")  # Replace with available ports dynamically if needed
        refresh_btn = QPushButton("Refresh")
        connect_btn = QPushButton("Connect")
        disconnect_btn = QPushButton("Disconnect")
        
        refresh_btn.clicked.connect(self.refresh)
        connect_btn.clicked.connect(self.connect_to_serial)
        disconnect_btn.clicked.connect(self.disconnect_serial)
        
        connection_layout.addWidget(self.port_combo)
        connection_layout.addWidget(refresh_btn)
        connection_layout.addWidget(connect_btn)
        connection_layout.addWidget(disconnect_btn)
        top_bar.addLayout(connection_layout)
        
        main_layout.addLayout(top_bar)
        
        # Tab bar (simulated with buttons)
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
        
        # Store mission time label as instance variable to update it
        self.mission_time_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        
        telemetry_fields = [
            ("Team ID:", "0001"),
            ("Mission Time:", self.mission_time_label),
            ("Parachute deployed:", "N"),
            ("Temperature:", "20"),
            ("Pressure:", "-22"),
            ("Camera 1 State:", "Disconnected"),
            ("Camera 2 State:", "Disconnected")
        ]
        
        for i, (label, value) in enumerate(telemetry_fields):
            telemetry_layout.addWidget(QLabel(label), i, 0)
            if isinstance(value, str):
                telemetry_layout.addWidget(QLabel(value), i, 1)
            else:
                telemetry_layout.addWidget(value, i, 1)
            
        telemetry_group.setLayout(telemetry_layout)
        content_layout.addWidget(telemetry_group)
        
        # Right panel - Graphs
        graphs_layout = QGridLayout()
        
        # Create graphs with titles
        graphs = [
            ("Pressure", "Pa"),
            ("Altitude", "m"),
            ("Tilt X", "deg"),
            ("Temperature", "°C"),
            ("Air speed", "m/s"),
            ("Tilt Y", "deg")
        ]
        
        for i, (title, unit) in enumerate(graphs):
            plot = pg.PlotWidget(title=f"{title} ({unit}) vs Time")  # Add title here
            plot.setBackground('w')
            plot.showGrid(x=True, y=True)
            plot.setLabel('left', f'{title} ({unit})')
            plot.setLabel('bottom', 'Time (s)')  # Changed from 'Packet' to 'Time (s)'
            
            # Customize title style
            plot.setTitle(f"{title} ({unit})", size="12pt")
            
            # Store plot reference
            setattr(self, f'{title.lower().replace(" ", "_")}_plot', plot)
            setattr(self, f'{title.lower().replace(" ", "_")}_curve', 
                   plot.plot(pen=pg.mkPen(color='b', width=2)))
            
            graphs_layout.addWidget(plot, i//3, i%3)
            
        content_layout.addLayout(graphs_layout)
        
        # Set content layout stretch
        content_layout.setStretchFactor(telemetry_group, 1)
        content_layout.setStretchFactor(graphs_layout, 4)
        
        main_layout.addLayout(content_layout)
        
        # Bottom bar - Command input
        bottom_layout = QHBoxLayout()
        cmd_input = QLineEdit()
        cmd_input.setPlaceholderText("CMD.0001...")
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

    def update_data(self):
        # Update mission time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.mission_time_label.setText(current_time)
        
        # Read data from serial port
        if self.serial_connection and self.serial_connection.is_open:
            try:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    data = line.split(',')  # Assuming data is comma-separated
                    self.serial_data_buffer.append(data)
                    self.update_graphs(data)
            except Exception as e:
                print(f"Error reading serial data: {e}")

    def update_graphs(self, data):
        # Map data to graphs dynamically
        try:
            for i, (title, _) in enumerate([
                ("Pressure", "Pa"),
                ("Altitude", "m"),
                ("Tilt X", "deg"),
                ("Temperature", "°C"),
                ("Air speed", "m/s"),
                ("Tilt Y", "deg")
            ]):
                plot_name = f'{title.lower().replace(" ", "_")}_curve'
                if hasattr(self, plot_name):
                    curve = getattr(self, plot_name)
                    y_data = [float(row[i]) for row in self.serial_data_buffer if len(row) > i]
                    x_data = range(len(y_data))
                    curve.setData(x_data, y_data)
        except Exception as e:
            print(f"Error updating graphs: {e}")

    def refresh(self):
        # Clear buffer and reset graphs
        self.serial_data_buffer = []
        for title, _ in [
            ("Pressure", "Pa"),
            ("Altitude", "m"),
            ("Tilt X", "deg"),
            ("Temperature", "°C"),
            ("Air speed", "m/s"),
            ("Tilt Y", "deg")
        ]:
            plot_name = f'{title.lower().replace(" ", "_")}_curve'
            if hasattr(self, plot_name):
                curve = getattr(self, plot_name)
                curve.setData([], [])

    def disconnect_serial(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Serial connection closed.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    main_window = CanSatGroundControl()
    main_window.show()
    sys.exit(app.exec_())
