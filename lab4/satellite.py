import pykka

from satellite_api import SatelliteAPI


class Satellite(pykka.ThreadingActor):

    def __init__(self, idx):
        super().__init__()
        self.id = id

    def get_status(self):
        return SatelliteAPI.get_status(self.id)
