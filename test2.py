# Working Code for Seperate graphs-img2


import sys
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGroupBox, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer
import os

class GroundSystemControlSystem(QMainWindow):
    def __init__(self):
        super().__init__()

        # Check if the CSV file exists and is not empty
        if os.path.exists('sensor_data.csv') and os.path.getsize('sensor_data.csv') > 0:
            self.df = pd.read_csv('sensor_data.csv')  # Read CSV data
        else:
            print("CSV file is empty or not found!")
            self.df = pd.DataFrame()  # Empty dataframe as fallback

        # Initialize UI components
        self.initUI()

        # Set up a timer to update the graphs periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1000)  # Update every second

        # Initialize the index for data rows
        self.index = 0

    def initUI(self):
        # Set up the main window
        self.setWindowTitle("Ground System Control System (GCS)")
        self.setGeometry(100, 100, 800, 600)

        # Create a widget and layout for the main window
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        # Create a QGroupBox for organizing the graphs
        group_box = QGroupBox("Sensor Data", self)
        group_layout = QVBoxLayout(group_box)

        # Create QGroupBox for each sensor's plot
        self.create_sensor_plot(group_layout, 'Pressure', 'r')
        self.create_sensor_plot(group_layout, 'Temperature', 'g')
        self.create_sensor_plot(group_layout, 'TiltX', 'b')
        self.create_sensor_plot(group_layout, 'TiltY', 'y')

        # Set up the layout and central widget
        main_layout.addWidget(group_box)
        self.setCentralWidget(central_widget)

    def create_sensor_plot(self, layout, label, color):
        # Create a new group box for the sensor
        sensor_group = QGroupBox(label, self)
        sensor_layout = QVBoxLayout(sensor_group)

        # Create a label to display above the graph
        sensor_label = QLabel(f'{label} Sensor Data', self)
        sensor_layout.addWidget(sensor_label)

        # Create a plot widget
        plot_widget = pg.PlotWidget(self)
        plot_widget.setLabel('left', label)
        plot_widget.setLabel('bottom', 'Time (s)')
        plot_widget.showGrid(x=True, y=True)
        
        # Create the curve for the sensor
        plot_curve = plot_widget.plot(pen=color, name=label)

        # Add the plot widget to the layout
        sensor_layout.addWidget(plot_widget)
        
        # Add the sensor group to the main layout
        layout.addWidget(sensor_group)

        # Store the plot curve for later updates
        setattr(self, f'{label.lower()}_curve', plot_curve)

    def update_graph(self):
        # Update the graph data from the CSV file for each sensor
        if self.index < len(self.df):
            # Extract the sensor data
            pressure = self.df.iloc[self.index]['Pressure']
            temperature = self.df.iloc[self.index]['Temperature']
            tilt_x = self.df.iloc[self.index]['TiltX']
            tilt_y = self.df.iloc[self.index]['TiltY']

            # Update the graph with the new data
            self.pressure_curve.setData(self.df['Time'][:self.index + 1], self.df['Pressure'][:self.index + 1])
            self.temperature_curve.setData(self.df['Time'][:self.index + 1], self.df['Temperature'][:self.index + 1])
            self.tiltx_curve.setData(self.df['Time'][:self.index + 1], self.df['TiltX'][:self.index + 1])
            self.tilty_curve.setData(self.df['Time'][:self.index + 1], self.df['TiltY'][:self.index + 1])

            # Increase the index to move to the next row of data
            self.index += 1
        else:
            # If the data is finished, stop the timer
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = GroundSystemControlSystem()  # Instantiate the main window
    main_window.show()
    sys.exit(app.exec_())
