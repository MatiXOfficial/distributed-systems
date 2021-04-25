import pykka
import time

from dispatcher_requests import SatErrorsRequest, SatStatusRequest

class MonitoringStation(pykka.ThreadingActor):

    def __init__(self, name, dispatcher, print_lock):
        super().__init__()
        self.name = name
        self.dispatcher = dispatcher
        self.print_lock = print_lock
        self.query_id = 1

    def ask_sat_status(self, first_sat_id, sat_range, timeout):
        request = SatStatusRequest(self.query_id, first_sat_id, sat_range, timeout)
        self.query_id += 1
        start_time = time.time()
        response = self.dispatcher.request_sat_status(request).get().get()
        end_time = time.time()

        self.print_lock.acquire()
        print(f'====== Station {self.name} ({response.query_id}) ======')
        print(f'time: {((end_time - start_time) * 1000):0.0f} ms')
        print(f'in time: {(response.in_time_rate * 100):.2f} %')
        print(f'errors: {len(response.sat_error_dict)}')
        for id, error in response.sat_error_dict.items():
            print(f'  {id}: {error}')
        print('================================')
        self.print_lock.release()

    def ask_sat_errors(self, id):
        request = SatErrorsRequest(id)
        self.dispatcher.request_sat_errors(request)
        response = self.dispatcher.request_sat_errors(request).get().get()
        
        if response.count > 0:
            if response.count == 1:
                self.print_lock.acquire()
                print(f'{response.id}: {response.count} error')
                self.print_lock.release()
            else:
                self.print_lock.acquire()
                print(f'{response.id}: {response.count} errors')
                self.print_lock.release()
