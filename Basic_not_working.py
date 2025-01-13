import sys
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import os

# New change
# Define a class
class GroundSystemControlSystem:
    def __init__(self):
        # Use 'self' within a class method
        self.df = pd.read_csv('sensor_data.csv')

    def display_data(self):
        # A method to display the first few rows of data
        print(self.df.head())

# Create an instance of the class
if __name__ == "__main__":
    main_window = GroundSystemControlSystem()  # Instantiate the class
    main_window.display_data()  # Display the data using a class method
# New change ends
if os.path.exists('sensor_data.csv') and os.path.getsize('sensor_data.csv') > 0:
    self.df = pd.read_csv('sensor_data.csv')
else:
    print("CSV file is empty or not found!")

class GroundSystemControlSystem(QMainWindow):
    def __init__(self):
        self.df = pd.read_csv('sensor_data.csv')  # Correct: 'self' is used inside a class method
        
        # Initialize UI components
        self.initUI()
        
        # Set up timer to update graphs periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1000)  # Update every second

        # Initialize data frame to hold CSV data
        self.df = pd.read_csv('sensor_data.csv')  # Assuming the data is in 'sensor_data.csv'

        # Initialize the index for data rows
        self.index = 0
        
    def initUI(self):
        # Set up main window
        self.setWindowTitle("Ground System Control System")
        self.setGeometry(100, 100, 800, 600)
        
        # Create a widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        # Create plot window using pyqtgraph
        self.plot_widget = pg.PlotWidget(self)
        layout.addWidget(self.plot_widget)

        # Create curve for each sensor
        self.pressure_curve = self.plot_widget.plot(pen='r', name="Pressure")
        self.temperature_curve = self.plot_widget.plot(pen='g', name="Temperature")
        self.tiltx_curve = self.plot_widget.plot(pen='b', name="TiltX")
        self.tilty_curve = self.plot_widget.plot(pen='y', name="TiltY")
        
        # Set up labels and grid
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.showGrid(x=True, y=True)

        # Set the central widget and layout
        self.setCentralWidget(central_widget)

    def update_graph(self):
        # Update the data from the CSV file for each sensor
        if self.index < len(self.df):
            pressure = self.df.iloc[self.index]['Pressure']
            temperature = self.df.iloc[self.index]['Temperature']
            tilt_x = self.df.iloc[self.index]['TiltX']
            tilt_y = self.df.iloc[self.index]['TiltY']
            
            # Update the graph with the new data
            self.pressure_curve.setData(self.df['Time'][:self.index+1], self.df['Pressure'][:self.index+1])
            self.temperature_curve.setData(self.df['Time'][:self.index+1], self.df['Temperature'][:self.index+1])
            self.tiltx_curve.setData(self.df['Time'][:self.index+1], self.df['TiltX'][:self.index+1])
            self.tilty_curve.setData(self.df['Time'][:self.index+1], self.df['TiltY'][:self.index+1])
            
            # Increase the index to move to the next row of data
            self.index += 1
        else:
            # If the data is finished, stop the timer
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = GroundSystemControlSystem()
    main_window.show()
    sys.exit(app.exec_())
