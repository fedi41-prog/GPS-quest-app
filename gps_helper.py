from kivy.app import App
from kivy.clock import mainthread
from kivy.utils import platform

from plyer import gps

from math import radians, cos, sqrt, sin, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Erdradius in Kilometern

    phi1 = radians(lat1)
    phi2 = radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

class GpsHelper:
    def __init__(self):
        print("starting GpsHelper...")

        self.app = App.get_running_app()

        self.target_lat = 52.5200  # Standard-Ziel: Berlin
        self.target_lon = 13.4050

        self.lat = None
        self.lon = None

        if platform == "android":
            from android.permissions import request_permissions, Permission
            print("running on Android: requesting permissions...")
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ])
        if platform == "android" or platform == "ios":
            try:
                gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
                gps.start(minTime=1000, minDistance=0)
                self.app.screen.updateLabel("GPS gestartet...")
            except NotImplementedError:
                self.app.screen.updateLabel("GPS is not implemented on your platform")


    def update_target(self, new_lat, new_lon):
        self.target_lat = new_lat
        self.target_lon = new_lon

    @mainthread
    def on_gps_location(self, *args, **kwargs):
        lat = kwargs['lat']
        lon = kwargs['lon']

        self.lat = lat
        self.lon = lon

        dist = haversine(lat, lon, self.target_lat, self.target_lon)
        self.app.screen.updateLabel(f"Ziel: {self.target_lat:.4f}, {self.target_lon:.4f}\n"
                                     f"Du bist {dist:.2f} km entfernt.")

    def on_gps_status(self, stype, status):
        print("GPS-Status:", stype, status)

    def stop(self):
        gps.stop()




