import logging
from enum import Enum


class RegistrationStatus(Enum):
    COMPLETED = 0
    SALES_ENDED = 1
    SOLD_OUT = 2
    NOT_ENOUGH_SEATS = 3


class EventTopic:
    PROGRESS = "progress"


log_levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
