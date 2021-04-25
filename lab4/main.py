import random
import threading
import time

from dispatcher import Dispatcher
from monitoring_station import MonitoringStation


if __name__ == '__main__':

    print_lock = threading.Lock()

    # dispatcher
    dispatcher = Dispatcher.start().proxy()

    # monitoring stations
    stations = [
        MonitoringStation.start('First', dispatcher, print_lock).proxy(),
        MonitoringStation.start('Second', dispatcher, print_lock).proxy(),
        MonitoringStation.start('Third', dispatcher, print_lock).proxy()
    ]
    
    try:
        # task 1.
        futures = []
        for station in stations:
            futures += [station.ask_sat_status(100 + random.randrange(50), 50, 300)]
            futures += [station.ask_sat_status(100 + random.randrange(50), 50, 300)]

        # wait till the end
        for future in futures:
            future.get()

        # task 2.
        time.sleep(1)
        for id in range(100, 200):
            stations[0].ask_sat_errors(id).get()

    finally:
        # stop
        dispatcher.stop()

        for station in stations:
            station.stop()
