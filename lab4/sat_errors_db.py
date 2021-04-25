import pykka
import sqlite3

from dispatcher_requests import SatErrorsRequest, SatErrorsResponse

class SatErrorsDB(pykka.ThreadingActor):

    def __init__(self, file_name='sat_errors.db'):
        super().__init__()
        self.conn = sqlite3.connect(file_name, check_same_thread=False)
        self.c = self.conn.cursor()

        # init the DB
        with self.conn:
            self.c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='sat_errors'")
            if self.c.fetchone()[0] == 0:  # table does not exist, create a new one
                self.c.execute("CREATE TABLE sat_errors (id integer, count integer)") 
            else:                          # table exists, clear it
                self.c.execute("DELETE FROM sat_errors")

            for id in range(100, 200):
                self.c.execute("INSERT INTO sat_errors VALUES (:id, 0)", {'id': id})

    def request_sat_errors(self, request: SatErrorsRequest):
        self.c.execute("SELECT count from sat_errors WHERE id = :id", {'id': request.id})
        return SatErrorsResponse(request.id, self.c.fetchone()[0])

    def add_error(self, id):
        with self.conn:
            self.c.execute("UPDATE sat_errors SET count = (count + 1) WHERE id = :id", {'id': id})

    def stop(self):
        self.conn.close()
        super().stop()