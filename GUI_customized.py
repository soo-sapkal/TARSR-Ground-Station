import sys
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QGroupBox, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, 
    QGridLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPixmap
import os
from datetime import datetime

class CanSatGroundControl(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize data
        self.load_data()
        
        self.initUI()
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second
        self.index = 0

    def load_data(self):
        """Loads data from the CSV file or initializes an empty DataFrame."""
        if os.path.exists('sensor_data.csv') and os.path.getsize('sensor_data.csv') > 0:
            self.df = pd.read_csv('sensor_data.csv')
        else:
            self.df = pd.DataFrame()

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
        
        # Logo
        logo_label = QLabel()
        logo_path = "logo.png"  # Replace with your logo path
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(50, 50)
        logo_label.setStyleSheet("border: 1px solid #ccc;")
        
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
        self.port_combo.addItem("ttyACM0")
        refresh_btn = QPushButton("Refresh")
        connect_btn = QPushButton("Connect")
        disconnect_btn = QPushButton("Disconnect")
        
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
            plot = pg.PlotWidget(title=f"{title} ({unit}) vs Time")
            plot.setBackground('w')
            plot.showGrid(x=True, y=True)
            plot.setLabel('left', f'{title} ({unit})')
            plot.setLabel('bottom', 'Time (s)')
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
        
        # Connect the refresh button
        refresh_btn.clicked.connect(self.refresh_application)

    def refresh_application(self):
        """Resets the application state and starts graph plotting from the beginning."""
        self.load_data()
        self.index = 0
        
        # Reset all graph curves to empty
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
        
        # Restart the update timer
        self.timer.start(1000)

    def update_data(self):
        """Updates the mission time and graphs with new data."""
        # Update mission time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.mission_time_label.setText(current_time)
        
        if self.index < len(self.df):
            # Update graphs
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
                    column = title.replace(" ", "")
                    if column in self.df.columns:
                        curve.setData(
                            self.df.index[:self.index + 1],
                            self.df[column][:self.index + 1]
                        )
            
            self.index += 1
        else:
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    main_window = CanSatGroundControl()
    main_window.show()
    sys.exit(app.exec_())