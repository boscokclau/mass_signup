import argparse
import sys
import csv
import logging.config
import yaml
from pubsub import pub
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog

import mass_signup_lib
import mass_signup
import ui_lib
from constants import EventTopic
from buyer import Buyer

# Application settings
USER_HOME_DIR = str(Path.home())
GROUP_SIZE = 10
DEFAULT_ORG_URL = "https://mountvirgin.eventbrite.com"
BUYER_FILE_PATH = "buyer_olmv.csv"


class Ui(QtWidgets.QMainWindow):
    def __init__(self, org_url: str, buyer_file_path: str, headless: bool = True, process_all_by: int = GROUP_SIZE):
        super(Ui, self).__init__()

        self.org_url = org_url
        self.buyer_file_path = buyer_file_path
        self.headless = headless
        self.process_all_by = process_all_by

        # Load UI file
        uic.loadUi("mass_signup.ui", self)

        # Widget handles
        self.cboEventUrl = self.findChild(QtWidgets.QComboBox, 'cboEventUrl')
        self.txtAttendeesFilePath = self.findChild(QtWidgets.QLineEdit, 'txtAttendeesFilePath')
        self.btnLoadAttendees = self.findChild(QtWidgets.QPushButton, 'btnLoadAttendees')
        self.btnPlaceOrder = self.findChild(QtWidgets.QPushButton, 'btnPlaceOrder')

        # Load initial data
        # Buyer
        buyer_firstname = None
        buyer_lastname = None
        buyer_email = None

        with open(self.buyer_file_path, 'r') as f:
            buyer_firstname, buyer_lastname, buyer_email = next(csv.reader(f))
            print(buyer_firstname, buyer_lastname, buyer_email)

        self.buyer = Buyer(buyer_firstname, buyer_lastname, buyer_email)
        self.lblBuyerName.setText(f"{self.buyer.first_name} {self.buyer.last_name}")

        events = ui_lib.get_active_events(self.org_url)
        events.sort(key=lambda x: x['event_name'])

        for event in events:
            self.cboEventUrl.addItem(event['event_name'], event)

        # Custom connects
        self.btnLoadAttendees.clicked.connect(self.openCsvSelectFileDialog)
        self.btnPlaceOrder.clicked.connect(self.placeOrder)

        self.txtAttendeesFilePath.textChanged.connect(self.stateChangeBtnPlaceOrder)

    def openCsvSelectFileDialog(self):
        file_path = QFileDialog.getOpenFileName(self, "", USER_HOME_DIR, "CSV (*.csv)")
        self.txtAttendeesFilePath.setText(file_path[0])

    def stateChangeBtnPlaceOrder(self):
        self.btnPlaceOrder.setEnabled(True if len(self.txtAttendeesFilePath.text()) else False)

    def placeOrder(self):
        event_url = self.cboEventUrl.itemData(self.cboEventUrl.currentIndex())['event_url']
        print(event_url)
        csv_path = self.txtAttendeesFilePath.text()
        attendee_list_collection = mass_signup_lib.get_attendees_from_csv(csv_path, process_all_by=self.process_all_by)

        status_all = 0
        # TODO: Print this to UI
        print("Processing {} order{}:".format(len(attendee_list_collection),
                                              "" if len(attendee_list_collection) == 1 else "s"))
        for i, attendee_list in enumerate(attendee_list_collection):
            # TODO: Print this to UI
            print("Order:", i + 1)
            status, info_dict = mass_signup.signup(attendee_list, self.buyer, event_url, headless=self.headless)

            # status != 0 means something might have gone wrong. Set bit to indicate which order had a problem
            if status:
                status_all = status_all | 1 << i

            # TODO: Print this to UI
            print("status, order_id: ", status, ",", str(info_dict))


# Progress messages subscription and print()
def print_progress(msg: str):
    print("Progress Message:", msg)


pub.subscribe(print_progress, EventTopic.PROGRESS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gui-mode', dest='gui_on', help='Show browser.',
                        action='store_true')
    parser.add_argument('-a', '--all_by', dest='process_all_by', default=0, help='Process all attendees by group of')
    parser.add_argument('-u', '--url', dest='url', default=None, help='Eventbrite Organizer URL')
    parser.add_argument('-b', '--buyer', dest='buyer', default=None, help='Buyer file path')

    args = parser.parse_args()

    # Log settings
    logging.config.dictConfig(yaml.safe_load(open('ui_logging.conf', 'r')))
    logger = logging.getLogger(EventTopic.PROGRESS)

    app = QtWidgets.QApplication(sys.argv)

    org_url = args.url if args.url else DEFAULT_ORG_URL
    headless = not args.gui_on if args.gui_on else True
    process_all_by = args.process_all_by if args.process_all_by else GROUP_SIZE
    buyer_file_path = args.buyer if args.buyer else BUYER_FILE_PATH

    window = Ui(org_url, buyer_file_path, headless=headless, process_all_by=process_all_by)
    window.show()
    app.exec()
