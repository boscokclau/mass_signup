import argparse
import sys
import csv
import logging.config
import yaml
from pubsub import pub
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal, QObject

import mass_signup_lib
import mass_signup
import ui_lib
from ui_lib import display_message
from constants import EventTopic
from buyer import Buyer

# Application settings
USER_HOME_DIR = str(Path.home())
GROUP_SIZE = 10
DEFAULT_ORG_URL = "https://mountvirgin.eventbrite.com"
BUYER_FILE_PATH = "buyer_olmv.csv"


class Message_Update(QObject):
    message_received = pyqtSignal(str)


class OrderRunner(QtCore.QThread):
    def __init__(self, ui, parent=None):
        super(OrderRunner, self).__init__(parent)
        self.ui = ui

    def run(self):
        # logger
        logger = logging.getLogger(__name__)

        event_url = self.ui.cboEventUrl.itemData(self.ui.cboEventUrl.currentIndex())['event_url']
        logger.debug(event_url)
        csv_path = self.ui.txtAttendeesFilePath.text()
        attendee_list_collection = mass_signup_lib.get_attendees_from_csv(csv_path,
                                                                          process_all_by=self.ui.process_all_by)

        status_all = 0

        display_message(
            f"Processing {len(attendee_list_collection)} order{'' if len(attendee_list_collection) == 1 else 's'}")

        for i, attendee_list in enumerate(attendee_list_collection):

            display_message(f"Order: {i + 1}")

            status, info_dict = mass_signup.signup(attendee_list, self.ui.buyer, event_url, headless=self.ui.headless)

            # status != 0 means something might have gone wrong. Set bit to indicate which order had a problem
            if status:
                status_all = status_all | 1 << i

            logger.debug(f"status, order_id: {status}, {info_dict}")


class Ui(QtWidgets.QMainWindow):
    def __init__(self, org_url: str, buyer_file_path: str, headless: bool = True, process_all_by: int = GROUP_SIZE):
        super(Ui, self).__init__()

        logger = logging.getLogger(__name__)

        self.org_url = org_url
        self.buyer_file_path = buyer_file_path
        self.headless = headless
        self.process_all_by = process_all_by

        # Order runner
        self.order_runner = None

        # Load UI file
        uic.loadUi("mass_signup.ui", self)

        # Widget handles
        self.cboEventUrl = self.findChild(QtWidgets.QComboBox, 'cboEventUrl')
        self.txtAttendeesFilePath = self.findChild(QtWidgets.QLineEdit, 'txtAttendeesFilePath')
        self.btnLoadAttendees = self.findChild(QtWidgets.QPushButton, 'btnLoadAttendees')
        self.btnPlaceOrder = self.findChild(QtWidgets.QPushButton, 'btnPlaceOrder')
        self.txtProgressMessage = self.findChild(QtWidgets.QPlainTextEdit, 'txtProgressMessage')

        # Load initial data
        # Buyer
        buyer_firstname = None
        buyer_lastname = None
        buyer_email = None

        with open(self.buyer_file_path, 'r') as f:
            buyer_firstname, buyer_lastname, buyer_email = next(csv.reader(f))

        self.buyer = Buyer(buyer_firstname, buyer_lastname, buyer_email)
        self.lblBuyerName.setText(f"{self.buyer.first_name} {self.buyer.last_name}")

        events = ui_lib.get_active_events(self.org_url)
        events.sort(key=lambda x: x['event_name'])

        for event in events:
            self.cboEventUrl.addItem(event['event_name'], event)

        # Custom connects
        self.btnLoadAttendees.clicked.connect(self.openCsvSelectFileDialog)
        self.btnPlaceOrder.clicked.connect(self.placeOrder)

        self.message_update = Message_Update()
        self.message_update.message_received.connect(self.updateProgressDialog)

        self.txtAttendeesFilePath.textChanged.connect(self.stateChangeBtnPlaceOrder)

        # Subscribe to display_message event
        pub.subscribe(self.process_message_event, EventTopic.PROGRESS)
        pub.subscribe(self.process_message_event, EventTopic.DISPLAY_MESSAGE)

    """ ----------------------
        Slots
        ----------------------
    """

    def openCsvSelectFileDialog(self):
        file_path = QFileDialog.getOpenFileName(self, "", USER_HOME_DIR, "CSV (*.csv)")
        self.txtAttendeesFilePath.setText(file_path[0])

    def stateChangeBtnPlaceOrder(self):
        self.btnPlaceOrder.setEnabled(True if len(self.txtAttendeesFilePath.text()) else False)

    def updateProgressDialog(self, msg: str):
        self.txtProgressMessage.textCursor().insertText(msg + "\n")

    def placeOrder(self):
        self.order_runner = OrderRunner(self)
        self.order_runner.start()

    """ ----------------------
        Event processors
        ----------------------
    """

    def process_message_event(self, msg: str):
        self.message_update.message_received.emit(msg)


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
    logger_progress = logging.getLogger(EventTopic.PROGRESS)
    logger_self = logging.getLogger(__name__)

    app = QtWidgets.QApplication(sys.argv)

    org_url = args.url if args.url else DEFAULT_ORG_URL
    headless = not args.gui_on if args.gui_on else True
    process_all_by = args.process_all_by if args.process_all_by else GROUP_SIZE
    buyer_file_path = args.buyer if args.buyer else BUYER_FILE_PATH

    window = Ui(org_url, buyer_file_path, headless=headless, process_all_by=process_all_by)
    window.show()
    app.exec()
