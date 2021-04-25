import pykka
import threading

from satellite import Satellite
from satellite_api import Status
from dispatcher_requests import *


class DispatcherWorker(pykka.ThreadingActor):

    def __init__(self, sat_errors_db, request: SatStatusRequest):
        super().__init__()
        self.sat_errors_db = sat_errors_db
        self.request = request
        self.range_start = request.first_sat_id
        self.range_end = self.range_start + request.sat_range
        self.in_time_count = 0
        self.response = SatStatusResponse(request.query_id)

    def gather_sat_status(self):
        # new thread for each satellite
        threads = []
        for i in range(self.range_start, self.range_end):
            new_thread = threading.Thread(target=self._thread_function, args=(i, ))
            new_thread.start()
            threads += [new_thread]

        for thread in threads:
            thread.join()
        
        self.response.in_time_rate = self.in_time_count / self.request.sat_range

        return self.response

    def _thread_function(self, id):
        satellite = Satellite.start(id).proxy()
        try:
            status = satellite.get_status().get(timeout=self.request.timeout / 1000)
            self.in_time_count += 1
            if status is not Status.OK:
                self.response.sat_error_dict[id] = status  # set status in the response
                self.sat_errors_db.add_error(id)  # add error to the DB
        
        except pykka.Timeout:
            pass

        finally:
            satellite.stop()
