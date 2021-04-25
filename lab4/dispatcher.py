import pykka

from sat_errors_db import SatErrorsDB
from dispatcher_requests import *
from dispatcher_worker import DispatcherWorker


class Dispatcher(pykka.ThreadingActor):

    def __init__(self):
        super().__init__()
        self.sat_errors_db = SatErrorsDB.start().proxy()

    def request_sat_status(self, request: SatStatusRequest):
        worker = DispatcherWorker.start(self.sat_errors_db, request).proxy()
        future = worker.gather_sat_status()
        worker.stop()
        return future
        
    def request_sat_errors(self, request: SatErrorsRequest):
        count = self.sat_errors_db.get_count_for_id(request.id).get()
        return SatErrorsResponse(request.id, count)

    def stop(self):
        self.sat_errors_db.stop()
        super().stop()
