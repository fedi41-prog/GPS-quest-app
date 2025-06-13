from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.utils import platform

if platform == "android":
    from plyer import gps, vibrator

from math import radians, cos, sqrt, sin, atan2

def haversine(lat1, lon1, lat2, lon2):
    # Erdmittelradius in Metern (WGS84-Durchschnittswert)
    R = 6378137.0

    # Koordinaten in Bogenmaß umrechnen
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    # Haversine-Formel
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Entfernung in Metern, dann in Zentimetern
    distance_m = R * c
    distance_cm = distance_m * 100
    return distance_cm

class GpsHelper:
    def __init__(self):

        self.app = App.get_running_app()

        self.target_lat = self.app.quest[self.app.level]["lat"]
        self.target_lon = self.app.quest[self.app.level]["lon"]
        self.target_radius = 4
        self.distances = self.app.quest[self.app.level]["distances"]

        self.border = self.app.quest[self.app.level]["border"]

        self.app.screen.updateMiddleLabel(self.app.quest[self.app.level]["text"])

        self.lat = None
        self.lon = None

        self.state = None

        self.shown = set()

        if platform == "android":
            from android.permissions import request_permissions, Permission
            print("running on Android: requesting permissions...")
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION,
                Permission.VIBRATE
            ])
        if platform == "android" or platform == "ios":
            try:
                gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
                gps.start(minTime=1000, minDistance=0)
            except NotImplementedError:
                print("GPS is not implemented on your platform")

    def update_target(self):
        self.target_lat = self.app.quest[self.app.level]["lat"]
        self.target_lon = self.app.quest[self.app.level]["lon"]
        self.target_radius = 4
        self.distances = self.app.quest[self.app.level]["distances"]

        self.border = self.app.quest[self.app.level]["border"]

        self.app.screen.updateMiddleLabel(self.app.quest[self.app.level]["text"])

        self.shown = set()


    @mainthread
    def on_gps_location(self, *args, **kwargs):

        print("on gps location...")

        lat = kwargs['lat']
        lon = kwargs['lon']
        accuracy = kwargs.get('accuracy', 100)  # in m
        speed = kwargs.get('speed', 0)

        # Zu ungenau? Dann Status setzen und abbrechen
        if accuracy > 20:
            self.state = "kein_fix"
            self.app.screen.updateStatus("Warte auf besseres GPS")
            return

        # Entfernung berechnen
        entfernung_m = haversine(lat, lon, self.target_lat, self.target_lon) / 100  # in m

        # Zustand bestimmen
        if entfernung_m > self.border:
            self.state = "entfernt"
        else:
            for d in self.distances.keys():
                if entfernung_m < int(d):

                    self.in_radius(d)

                    break



        # Position speichern
        self.lat = lat
        self.lon = lon

        # Statusanzeige
        if self.state == "kein fix":
            status = "Warte auf besseres GPS"
        elif self.state == "entfernt":
            status = "Du bist zu weit weg!"
            if platform == "android":
                if vibrator.exists():
                    vibrator.vibrate(time=0.1)
        else:
            status = "..."
        self.app.screen.updateStatus(status)
        print(self.state)

    def in_radius(self, key):
        print("in range: " + key)

        if not self.app.screen.dialog_open and not key in self.shown:
            if platform == "android":
                if vibrator.exists():
                    vibrator.vibrate(time=0.3)

            if self.distances[key]["type"] == "hint":
                self.app.screen.show_hint_dialog(key)
            elif self.distances[key]["type"] == "choose":
                self.app.screen.show_multiple_choice_dialog(key)
            elif self.distances[key]["type"] == "text":
                self.app.screen.show_text_input_dialog(key)



    def on_gps_status(self, stype, status):
        print("GPS-Status:", stype, status)

    def stop(self):
        gps.stop()




