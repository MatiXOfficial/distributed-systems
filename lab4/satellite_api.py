from enum import Enum
import random
import time


class Status(Enum):
    OK = 0
    BATTERY_LOW = 1
    PROPULSION_ERROR = 2
    NAVIGATION_ERROR = 3


class SatelliteAPI:

    @staticmethod
    def get_status(satellite_index):
        time.sleep((100 + random.randrange(400)) / 1000)
        p = random.random()
        if p < 0.8:
            return Status.OK
        elif p < 0.9:
            return Status.BATTERY_LOW
        elif p < 0.95:
            return Status.NAVIGATION_ERROR
        else:
            return Status.PROPULSION_ERROR
