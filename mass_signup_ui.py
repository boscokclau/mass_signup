import sys
import csv
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
        self.txtAttendeesFilePath = self.findChild(QtWidgets.QLineEdit, 'txtAttendeesFilePath')
        self.txtBuyerFilePath = self.findChild(QtWidgets.QLineEdit, 'txtBuyerFilePath')
        self.btnLoadAttendees = self.findChild(QtWidgets.QPushButton, 'btnLoadAttendees')
        self.btnLoadBuyer = self.findChild(QtWidgets.QPushButton, 'btnLoadBuyer')
        self.btnPlaceOrder = self.findChild(QtWidgets.QPushButton, 'btnPlaceOrder')

        # Custom connects
        self.btnLoadAttendees.clicked.connect(self.openCsvSelectFileDialog)
        self.btnLoadBuyer.clicked.connect(self.openBuyerSelectFileDialog)
        self.btnPlaceOrder.clicked.connect(self.placeOrder)

    def openCsvSelectFileDialog(self):
        file_path = QFileDialog.getOpenFileName(self, "", USER_HOME_DIR, "CSV (*.csv)")
        self.txtAttendeesFilePath.setText(file_path[0])

    def openBuyerSelectFileDialog(self):
        file_path = QFileDialog.getOpenFileName(self, "", USER_HOME_DIR, "CSV (*.csv)")
        self.txtBuyerFilePath.setText(file_path[0])

    def placeOrder(self):
        # Buyer
        buyer_firstname = None
        buyer_lastname = None
        buyer_email = None

        buyer_path = self.txtBuyerFilePath.text()

        with open(buyer_path, 'r') as f:
            buyer_firstname, buyer_lastname, buyer_email = next(csv.reader(f))
            print(buyer_firstname, buyer_lastname, buyer_email)

        buyer = Buyer(buyer_firstname, buyer_lastname, buyer_email)

        event_url = self.txtEventUrl.text()
        csv_path = self.txtAttendeesFilePath.text()
        attendee_list_collection = mass_signup_lib.get_attendees_from_csv(csv_path, process_all_by=10)

        status_all = 0
        for i, attendee_list in enumerate(attendee_list_collection):
            # TODO: Print this to UI
            print("Order:", i + 1)
            status, info_dict = mass_signup.signup(attendee_list, buyer, event_url, headless=True)

            # status != 0 means something might have gone wrong. Set bit to indicate which order had a problem
            if status:
                status_all = status_all | 1 << i

            # TODO: Print this to UI
            print("status, order_id: ", status, ",", str(info_dict))


app = QtWidgets.QApplication(sys.argv)

window = Ui()
window.show()
app.exec()
