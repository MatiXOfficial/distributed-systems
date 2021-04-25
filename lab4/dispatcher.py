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
        future = worker.request_sat_status()
        worker.stop()
        return future
        
    def request_sat_errors(self, request: SatErrorsRequest):
        return self.sat_errors_db.request_sat_errors(request)

    def stop(self):
        self.sat_errors_db.stop()
        super().stop()
