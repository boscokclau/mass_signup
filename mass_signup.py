import sys
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog

# Application settings
USER_HOME_DIR = str(Path.home())


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("mass_signup.ui", self)

        # Widget handles
        self.txtCsvFilePath = self.findChild(QtWidgets.QLineEdit, 'txtCsvFilePath')
        self.btnCsvBrowse = self.findChild(QtWidgets.QPushButton, 'btnCsvBrowse')

        # Custom connects
        self.btnCsvBrowse.clicked.connect(self.openCsvSelectFileDialog)

    def openCsvSelectFileDialog(self):
        file_path = QFileDialog.getOpenFileName(self, "Select a CSV file", USER_HOME_DIR, "CSV (*.csv)")
        self.txtCsvFilePath.setText(file_path[0])


app = QtWidgets.QApplication(sys.argv)

window = Ui()
window.show()
app.exec()
