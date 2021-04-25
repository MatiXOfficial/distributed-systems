##### status #####
class SatStatusRequest:

    def __init__(self, query_id, first_sat_id, sat_range, timeout):
        self.query_id = query_id
        self.first_sat_id = first_sat_id
        self.sat_range = sat_range
        self.timeout = timeout


class SatStatusResponse:

    def __init__(self, query_id, sat_error_dict=None, in_time_rate=0):
        self.query_id = query_id
        if sat_error_dict is None:
            self.sat_error_dict = dict()
        else:
            self.sat_error_dict = sat_error_dict
        self.in_time_rate = in_time_rate

##### errors #####
class SatErrorsRequest:

    def __init__(self, id):
        self.id = id

class SatErrorsResponse:

    def __init__(self, id, count):
        self.id = id
        self.count = count
