import logging
from enum import Enum


class RegistrationStatus(Enum):
    COMPLETED = 0
    SALES_ENDED = 1
    SOLD_OUT = 2
    NOT_ENOUGH_SEATS = 3
    UNEXPECTED_ERROR = 4


class EventTopic:
    PROGRESS = "progress"
    DISPLAY_PROGRESS_MESSAGE = "display_progress_message"
    DISPLAY_ORDER_SUMMARY = "display_order_summary"


log_levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
