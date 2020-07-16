from enum import Enum


class RegistrationStatus(Enum):
    COMPLETED = 0
    SALES_ENDED = 1
    SOLD_OUT = 2
    NOT_ENOUGH_SEATS = 3
