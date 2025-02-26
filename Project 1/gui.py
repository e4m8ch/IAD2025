import sys
import serial
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, QLineEdit, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Aquisição de Dados - Raspberry Pi'
        self.initUI()
        self.initSerial()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.requestData)  # Timer para enviar comandos automaticamente

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(400, 400, 800, 400)

        # Criar widget central
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        # Layout principal
        self.globalLayout = QVBoxLayout(centralWidget)

        # Criar gráfico
        self.graphWidget = pg.PlotWidget()
        self.globalLayout.addWidget(self.graphWidget)

        # Layout de opções
        self.optionsLayout = QHBoxLayout()

        # Layout de entrada
        self.inputLayout = QVBoxLayout()
        self.label = QLabel('Intervalo de aquisição (ms):')
        self.inputLayout.addWidget(self.label)
        self.inputInterval = QLineEdit()
        self.inputInterval.setText("1000")  # Intervalo padrão: 1 segundo
        self.inputLayout.addWidget(self.inputInterval)
        self.optionsLayout.addLayout(self.inputLayout)

        # Layout de botões
        self.buttonLayout = QVBoxLayout()

        # Botão de iniciar/parar aquisição automática
        self.toggleButton = QPushButton('Iniciar Aquisição', self)
        self.toggleButton.clicked.connect(self.toggleAcquisition)
        self.buttonLayout.addWidget(self.toggleButton)

        # Botão de limpar gráfico
        self.clearButton = QPushButton('Limpar Gráfico', self)
        self.clearButton.clicked.connect(self.clearGraph)
        self.buttonLayout.addWidget(self.clearButton)

        self.optionsLayout.addLayout(self.buttonLayout)
        self.globalLayout.addLayout(self.optionsLayout)

        self.show()

    def initSerial(self):
        try:
            self.ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)  # AJUSTAR PARA PORTA CERTA
            time.sleep(2)  # Espera para estabilizar conexão
        except serial.SerialException:
            QMessageBox.critical(self, 'Erro de Conexão', 'Não foi possível abrir a porta serial.')
            sys.exit()

    def toggleAcquisition(self):
        if self.timer.isActive():
            self.timer.stop()
            self.toggleButton.setText('Iniciar Aquisição')
        else:
            try:
                interval = int(self.inputInterval.text())
                self.timer.start(interval)  # Inicia a aquisição automática
                self.toggleButton.setText('Parar Aquisição')
            except ValueError:
                QMessageBox.warning(self, 'Erro', 'Por favor, insira um número válido.')

    def requestData(self):
        self.ser.write(b'GET\n')  # Enviar comando GET para o Arduino

    def read_from_arduino(self):
        while self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line == "ERROR":
                    print("Comando inválido recebido pelo Arduino!")
                else:
                    value, timestamp = map(int, line.split(','))
                    print(f"Valor: {value}, Tempo: {timestamp}ms")
                    self.graphWidget.plot([timestamp], [value], pen='r', symbol='o')
            except Exception as e:
                print("Erro ao ler dados:", e)

    def clearGraph(self):
        self.graphWidget.clear()

    def closeEvent(self, event):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
