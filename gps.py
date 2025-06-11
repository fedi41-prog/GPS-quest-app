from kivy.clock import mainthread
from kivy.utils import platform
from kivy.app import App
from math import radians, cos, sqrt, sin, atan2

if platform == "android":
    from jnius import autoclass, PythonJavaClass, java_method
    from android.permissions import request_permissions, Permission

    # Android-Klassen
    Context = autoclass('android.content.Context')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    LocationManager = autoclass('android.location.LocationManager')

    class MyLocationListener(PythonJavaClass):
        __javainterfaces__ = ['android/location/LocationListener']
        __javacontext__ = 'app'

        def __init__(self, callback):
            super().__init__()
            self.callback = callback

        @java_method('(Landroid/location/Location;)V')
        def onLocationChanged(self, location):
            lat = location.getLatitude()
            lon = location.getLongitude()
            print(f"Neue Position empfangen: {lat}, {lon}")
            self.callback(lat, lon)

        @java_method('(Ljava/lang/String;)V')
        def onProviderDisabled(self, provider): pass

        @java_method('(Ljava/lang/String;)V')
        def onProviderEnabled(self, provider): pass

        @java_method('(Ljava/lang/String;ILandroid/os/Bundle;)V')
        def onStatusChanged(self, provider, status, extras): pass

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
        print("GpsHelper wird gestartet...")
        self.app = App.get_running_app()
        self.lat = None
        self.lon = None
        self.target_lat = 51.32715211249888
        self.target_lon = 12.33595049008727
        self.loc_service = None
        self.listener = None

        if platform != "android":
            print("Nicht Android – GPS nicht verfügbar.")
            self.app.screen.updateLabel("GPS nur auf Android verfügbar.")
            return

        # Rechte anfragen, und dann Callback aufrufen
        request_permissions(
            [Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION],
            self.on_permissions_granted
        )

    def on_permissions_granted(self, permissions, grants):
        if all(grants):
            print("GPS-Rechte gewährt.")
            self._init_android_gps()
        else:
            self.app.screen.updateLabel("GPS-Rechte wurden verweigert.")

    def _init_android_gps(self):
        try:
            self.activity = PythonActivity.mActivity
            self.loc_service = self.activity.getSystemService(Context.LOCATION_SERVICE)

            print("GPS enabled:", self.loc_service.isProviderEnabled(LocationManager.GPS_PROVIDER))
            print("Netzwerk enabled:", self.loc_service.isProviderEnabled(LocationManager.NETWORK_PROVIDER))

            self.listener = MyLocationListener(self.on_gps_location)

            provider = LocationManager.GPS_PROVIDER
            if not self.loc_service.isProviderEnabled(provider):
                provider = LocationManager.NETWORK_PROVIDER

            self.loc_service.requestLocationUpdates(
                provider,
                1000,
                0,
                self.listener
            )
            self.app.screen.updateLabel("GPS gestartet...")
        except Exception as e:
            print(f"GPS-Fehler: {e}")
            self.app.screen.updateLabel(f"Fehler beim Start des GPS: {e}")

    def update_target(self, new_lat, new_lon):
        self.target_lat = new_lat
        self.target_lon = new_lon

    @mainthread
    def on_gps_location(self, lat, lon):
        self.lat = lat
        self.lon = lon
        dist = haversine(lat, lon, self.target_lat, self.target_lon)
        self.app.screen.updateLabel(
            f"Ziel: {self.target_lat:.4f}, {self.target_lon:.4f}\n"
            f"Du bist {dist:.2f} m entfernt."
        )

        #self.app.screen.updateLabel(f"{lat} - {lon}")

    def stop(self):
        if platform == "android" and self.loc_service and self.listener:
            try:
                self.loc_service.removeUpdates(self.listener)
            except Exception as e:
                print(f"Fehler beim Stoppen des GPS: {e}")

    def get_last_known_location(self):
        location = self.loc_service.getLastKnownLocation(LocationManager.GPS_PROVIDER)
        if location:
            lat = location.getLatitude()
            lon = location.getLongitude()
            print(f"Letzte bekannte Position: {lat}, {lon}")
            self.on_gps_location(lat, lon)

