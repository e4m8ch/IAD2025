import sys
import serial
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QToolBar, QAction, QLabel, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


# Defines the Widget class for the stuff inside the window (graph and options)
class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Creates the layout for the graph and buttons
        self.globalLayout = QVBoxLayout(self)

        # Creates a graph widget
        self.graphWidget = pg.PlotWidget()
        self.globalLayout.addWidget(self.graphWidget)

        # Options layout
        self.optionsLayout = QHBoxLayout()

        # Input layout
        self.inputLayout = QVBoxLayout()

        # Timer for reading data from Arduino, this will be a set interval in which the program will acquire data from the Arduino
        self.label = QLabel('Please input the time interval to get data from Arduino, in seconds:')
        self.inputLayout.addWidget(self.label)
        self.inputInterval = QLineEdit()
        self.inputLayout.addWidget(self.inputInterval)
        self.optionsLayout.addLayout(self.inputLayout)


        # Button layout
        self.buttonLayout = QVBoxLayout()

        # Clear data button
        self.clearButton = QPushButton('Clear Data on Graph', self)
        self.clearButton.setToolTip('Send the command to the Arduino')
        self.clearButton.clicked.connect(self.clearGraph)
        self.buttonLayout.addWidget(self.clearButton)

        # Toggle acquisition button
        self.toggleButton = QPushButton('Toggle Data Aquisition', self)
        self.toggleButton.setToolTip('Send the command to the Arduino')
        self.toggleButton.clicked.connect(self.toggleDataAquisition)
        self.buttonLayout.addWidget(self.toggleButton)

        # Final laying out properties
        self.optionsLayout.addLayout(self.buttonLayout)
        self.globalLayout.addLayout(self.optionsLayout)

    def toggleDataAquisition(self):
        # Function that toggles the data acquisition from the Arduino
        pass

    def clearGraph(self):
        self.graphWidget.clear()  # Clear the graph

    def read_from_arduino(self):
        # Example function where you can read data from Arduino
        pass


# MainWindow class that adds the GraphWidget as the central widget
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Arduino Communication'
        self.initUI()
        self.initSerial()

    def initUI(self):
        """
        This code was supposed to add a toolbar to save and import graph data, but I later learned that it was not necessary, since
        pyQtGraph already has a built-in function to save the data from the graph.

        # Initialize the toolbar and set it to the main window
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)

        # Add toolbar to the main window
        self.addToolBar(self.toolbar)

        self.saveButton = QAction(QIcon(), "Save", self)
        self.saveButton.triggered.connect(self.save)
        self.toolbar.addAction(self.saveButton)

        self.importButton = QAction(QIcon(), "Import", self)
        self.importButton.triggered.connect(self.importData)
        self.toolbar.addAction(self.importButton)
        """

        # Set the main window title
        self.setWindowTitle(self.title)
        self.setGeometry(400, 400, 800, 400)

        # Create an instance of GraphWidget and set it as central widget
        graph_widget = GraphWidget()
        self.setCentralWidget(graph_widget)

        self.show()

    def initSerial(self):
        """
        try:
            # Adjust 'COM4' to your Arduino's serial port
            self.ser = serial.Serial('COM4', 88000, timeout=1)
            time.sleep(2)  # Wait for the Arduino to reset
        except serial.SerialException:
            QMessageBox.critical(self, 'Serial Connection Error', 'Could not open serial port.')
            sys.exit()
        """
        pass

    def closeEvent(self, event):
        """
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
        event.accept()
        """
        pass

    def save(self):
        # Save the data from the graph
        pass

    def importData(self):
        # Save the data from the graph
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow() 
    sys.exit(app.exec_())
