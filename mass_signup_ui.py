import sys
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog

import signup_csv

# Application settings
USER_HOME_DIR = str(Path.home())


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("mass_signup.ui", self)

        # Widget handles
        self.txtEventUrl = self.findChild(QtWidgets.QLineEdit, 'txtEventUrl')
        self.txtCsvFilePath = self.findChild(QtWidgets.QLineEdit, 'txtCsvFilePath')
        self.btnCsvBrowse = self.findChild(QtWidgets.QPushButton, 'btnCsvBrowse')
        self.btnPlaceOrder = self.findChild(QtWidgets.QPushButton, 'btnPlaceOrder')

        # Custom connects
        self.btnCsvBrowse.clicked.connect(self.openCsvSelectFileDialog)
        self.btnPlaceOrder.clicked.connect(self.placeOrder)

    def openCsvSelectFileDialog(self):
        file_path = QFileDialog.getOpenFileName(self, "Select a CSV file", USER_HOME_DIR, "CSV (*.csv)")
        self.txtCsvFilePath.setText(file_path[0])

    def placeOrder(self):
        event_url = self.txtEventUrl.text()
        csv_path = self.txtCsvFilePath.text()
        signup_csv.process_registration(event_url, csv_path, headless=True, process_all_by=10)


app = QtWidgets.QApplication(sys.argv)

window = Ui()
window.show()
app.exec()
