from math import radians, cos, sqrt, sin, atan2

import kivy

try:
    from android.permissions import request_permissions, Permission
    ANDROID = True
except ImportError:
    ANDROID = False
    # Dummy-Stubs, damit PyCharm nicht meckert
    def request_permissions(perms, callback=None):
        print("Mock request_permissions:", perms)
    class Permission:
        ACCESS_FINE_LOCATION = ""
        ACCESS_COARSE_LOCATION = ""
        WRITE_EXTERNAL_STORAGE = ""
        READ_EXTERNAL_STORAGE = ""

from kivy.lang import Builder
from plyer import gps

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

kivy.require("1.9.0")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Erdradius in Kilometern

    phi1 = radians(lat1)
    phi2 = radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def updateLabel(self, text):
        self.text_label.text = str(text)


class GpsQuestApp(MDApp):
    def build(self):
        if ANDROID:
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ])
        else:
            print("Running on Desktop, keine Laufzeit-Permissions nötig.")

        self.screen = Builder.load_file('gpsquestapp.kv')

        self.target_lat = 52.5200  # Standard-Ziel: Berlin
        self.target_lon = 13.4050

        try:
            gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
            gps.start(minTime=1000, minDistance=1)
        except NotImplementedError:
            self.screen.updateLabel("GPS nicht verfügbar")
        return self.screen

    def on_gps_location(self, **kwargs):
        lat = kwargs['lat']
        lon = kwargs['lon']

        self.last_lat = lat
        self.last_lon = lon

        dist = haversine(lat, lon, self.target_lat, self.target_lon)
        self.screen.updateLabel(f"Ziel: {self.target_lat:.4f}, {self.target_lon:.4f}\n"
                                     f"Du bist {dist:.2f} km entfernt.")

    def on_gps_status(self, stype, status):
        print("GPS-Status:", stype, status)

    def set_current_as_target(self):
        if hasattr(self, 'last_lat') and hasattr(self, 'last_lon'):
            self.target_lat = self.last_lat
            self.target_lon = self.last_lon
            self.screen.updateLabel("Neues Ziel gesetzt!")
        else:
            self.screen.updateLabel("Standort noch nicht verfügbar.")


if __name__ == "__main__":
    GpsQuestApp().run()