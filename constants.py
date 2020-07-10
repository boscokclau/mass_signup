from enum import Enum


class RegistrationStatus(Enum):
    COMPLETED = 0
    SOLD_OUT = 1
    NOT_ENOUGH_SEATS = 2
    TOO_MANY_REQUESTS = 3

class ProgramStatus(Enum):
    COMPLETED = 0
    FILE_NOT_FOUND = 1
    CONSTRAINT_VIOLATION = 2