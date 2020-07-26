#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import logging.config
import os
import sys
import yaml
from enum import Enum
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, pyqtSignal
from pathlib import Path
from pubsub import pub

import constants
import mass_signup_lib
import mass_signup
import ui_lib
from buyer import Buyer
from constants import EventTopic, RegistrationStatus
from ui_lib import display_progress_message

# Application settings
USER_HOME_DIR = str(Path.home())
GROUP_SIZE = 10
DEFAULT_ORG_URL = "https://mountvirgin.eventbrite.com"
BUYER_FILE_PATH = "buyer_olmv.csv"

# Log settings
logging.config.dictConfig(yaml.safe_load(open('ui_logging.conf', 'r')))
logger_progress = logging.getLogger(EventTopic.PROGRESS)
logger = logging.getLogger(os.path.basename(__file__))


class Order_State(Enum):
    READY = 0
    IN_PROGRESS = 1
    NOT_READY = 2
    COMPLETED = 3


class Order_Summary:
    def __init__(self, seq_id: int, registration_status: RegistrationStatus, info_dict: dict = dict()):
        self.seq_id = seq_id
        self.reg_status = registration_status
        self.info_dict = info_dict

    def __str__(self):
        if self.reg_status == RegistrationStatus.COMPLETED:
            return f"Order {self.seq_id:2d}: Order Number {self.info_dict['order_id']}"

        elif self.reg_status == RegistrationStatus.SALES_ENDED:
            return f"Order {self.seq_id:2d}: Sales Ended--No registration processed"

        elif self.reg_status == RegistrationStatus.SOLD_OUT:
            return f"Order {self.seq_id:2d}: Sold Out--No registration processed"

        elif self.reg_status == RegistrationStatus.NOT_ENOUGH_SEATS:
            return f"Order {self.seq_id:2d}: Not Enough Seats--Only {self.info_dict['remaining']} remained"
        else:
            return f"Order {self.seq_id:2d}: Error Occurred--No registration processed"


class UI_Signal(QObject):
    progress_message_received = pyqtSignal(str)
    order_state_changed = pyqtSignal(Order_State)
    order_summary_available = pyqtSignal(Order_Summary)


class OrderRunner(QtCore.QThread):
    def __init__(self, ui, parent=None):
        super(OrderRunner, self).__init__(parent)
        self.ui = ui

    def run(self):
        event_url = self.ui.cboEventUrl.itemData(self.ui.cboEventUrl.currentIndex())['event_url']
        logger.debug(f"Event URL: {event_url}")

        csv_path = self.ui.txtAttendeesFilePath.text()
        attendee_list_collection = mass_signup_lib.get_attendees_from_csv(csv_path,
                                                                          process_all_by=self.ui.process_all_by)

        status_all = 0

        display_progress_message(
            f"Processing {len(attendee_list_collection)} order{'' if len(attendee_list_collection) == 1 else 's'}")

        for i, attendee_list in enumerate(attendee_list_collection):

            display_progress_message(f"Order: {i + 1}")

            status, info_dict = mass_signup.signup(attendee_list, self.ui.buyer, event_url, headless=self.ui.headless)

            # status != 0 means something might have gone wrong. Set bit to indicate which order had a problem
            if status != RegistrationStatus.COMPLETED:
                status_all = status_all | 1 << i

            logger.debug(f"status, order_id: {status}, {info_dict}")
            self.ui.ui_signal.order_summary_available.emit(Order_Summary(i + 1, status, info_dict))

        self.ui.ui_signal.order_state_changed.emit(Order_State.COMPLETED)


class Ui(QtWidgets.QMainWindow):
    def __init__(self, org_url: str, buyer_file_path: str, headless: bool = True, process_all_by: int = GROUP_SIZE):
        super(Ui, self).__init__()

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
        self.txtOrderSummary = self.findChild(QtWidgets.QPlainTextEdit, 'txtOrderSummary')
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
        self.btnLoadAttendees.clicked.connect(self.open_csv_select_file_dialog)
        self.btnPlaceOrder.clicked.connect(self.place_order)

        self.ui_signal = UI_Signal()
        self.ui_signal.progress_message_received.connect(self.update_progress_message)
        self.ui_signal.order_state_changed.connect(self.process_order_state_change)
        self.ui_signal.order_summary_available.connect(self.update_order_summary)

        self.cboEventUrl.currentIndexChanged.connect(self.update_with_event_selection_changed)
        self.txtAttendeesFilePath.textChanged.connect(self.update_with_attendees_file_path_changed)

        # Subscribe to display_progress_message event
        pub.subscribe(self.process_message_event, EventTopic.PROGRESS)
        pub.subscribe(self.process_message_event, EventTopic.DISPLAY_PROGRESS_MESSAGE)
        pub.subscribe(self.process_order_summary_event, EventTopic.DISPLAY_ORDER_SUMMARY)

    """ ----------------------
        Slots
        ----------------------
    """

    def open_csv_select_file_dialog(self):
        file_path = QFileDialog.getOpenFileName(self, "", USER_HOME_DIR, "CSV (*.csv)")
        self.txtAttendeesFilePath.setText(file_path[0])

    def update_with_attendees_file_path_changed(self):
        if len(self.txtAttendeesFilePath.text()):
            self.ui_signal.order_state_changed.emit(Order_State.READY)
        else:
            self.ui_signal.order_state_changed.emit(Order_State.NOT_READY)

    def update_with_event_selection_changed(self):
        self.update_with_attendees_file_path_changed()

    def update_progress_message(self, msg: str):
        self.txtProgressMessage.textCursor().insertText(msg + "\n")
        self.txtProgressMessage.ensureCursorVisible()

    def update_order_summary(self, order_summary: Order_Summary):
        self.txtOrderSummary.textCursor().insertText(str(order_summary) + "\n")
        self.txtOrderSummary.ensureCursorVisible()

    def process_order_state_change(self, state: Order_State):
        if state == Order_State.COMPLETED:
            self.cboEventUrl.setEnabled(True)
            self.txtAttendeesFilePath.setEnabled(True)
            self.btnLoadAttendees.setEnabled(True)
            self.btnPlaceOrder.setText("Re-Order")
            self.btnPlaceOrder.setEnabled(True)

        elif state == Order_State.IN_PROGRESS:
            self.cboEventUrl.setEnabled(False)
            self.txtAttendeesFilePath.setEnabled(False)
            self.btnLoadAttendees.setEnabled(False)
            self.btnPlaceOrder.setText("In Progress")
            self.btnPlaceOrder.setEnabled(False)

        elif state == Order_State.READY:
            self.cboEventUrl.setEnabled(True)
            self.txtAttendeesFilePath.setEnabled(True)
            self.btnLoadAttendees.setEnabled(True)
            self.btnPlaceOrder.setText("Place Order")
            self.btnPlaceOrder.setEnabled(True)

        else:  # NOT_READY
            self.cboEventUrl.setEnabled(True)
            self.txtAttendeesFilePath.setEnabled(True)
            self.btnLoadAttendees.setEnabled(True)
            self.btnPlaceOrder.setText("Place Order")
            self.btnPlaceOrder.setEnabled(False)

        self.btnPlaceOrder.repaint()

    def place_order(self):
        self.ui_signal.order_state_changed.emit(Order_State.IN_PROGRESS)
        self.order_runner = OrderRunner(self)
        self.order_runner.start()

    """ ----------------------
        Event processors
        ----------------------
    """

    def process_message_event(self, msg: str):
        self.ui_signal.progress_message_received.emit(msg)

    def process_order_summary_event(self, info_dict: dict):
        self.ui_signal.order_summary_available(info_dict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gui-mode', dest='gui_on', help='Show browser.',
                        action='store_true')
    parser.add_argument('-a', '--all_by', dest='process_all_by', default=0, help='Process all attendees by group of')
    parser.add_argument('-u', '--url', dest='url', default=None, help='Eventbrite Organizer URL')
    parser.add_argument('-b', '--buyer', dest='buyer', default=None, help='Buyer file path')
    parser.add_argument('-l', '-loglevel', dest='log_level',
                        choices=['critical', 'error', 'warning', 'info', 'debug'], default='warning',
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)

    org_url = args.url if args.url else DEFAULT_ORG_URL
    headless = not args.gui_on if args.gui_on else True
    process_all_by = args.process_all_by if args.process_all_by else GROUP_SIZE
    buyer_file_path = args.buyer if args.buyer else BUYER_FILE_PATH

    log_level = constants.log_levels[args.log_level]
    logger.setLevel(log_level)

    window = Ui(org_url, buyer_file_path, headless=headless, process_all_by=process_all_by)
    window.show()
    app.exec()
