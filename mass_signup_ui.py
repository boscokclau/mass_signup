import sys
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog

import mass_signup_lib
import mass_signup
from buyer import Buyer

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
        # TODO: Save buyer information on disk
        # Buyer is always the OLMV Mass EB organizer
        buyer_FN = "OLMV"
        buyer_LN = "Seattle"
        buyer_email = "olmv.seattle@gmail.com"

        buyer = Buyer(buyer_FN, buyer_LN, buyer_email)

        event_url = self.txtEventUrl.text()
        csv_path = self.txtCsvFilePath.text()
        attendee_list_collection = mass_signup_lib.get_attendees_from_csv(csv_path, process_all_by=10)

        status_all = 0
        for i, attendee_list in enumerate(attendee_list_collection):
            # TODO: Print this to UI
            print("Order:", i + 1)
            status, order_id = mass_signup.signup(attendee_list, buyer, event_url, headless=True)

            # status != 0 means something might have gone wrong. Set bit to indicate which order had a problem
            if status:
                status_all = status_all | 1 << i

            # TODO: Print this to UI
            print("status, order_id: ", status, ",", order_id)


app = QtWidgets.QApplication(sys.argv)

window = Ui()
window.show()
app.exec()
