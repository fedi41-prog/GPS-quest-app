
import kivy

from kivy.lang import Builder

from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from gps_helper import GpsHelper

kivy.require("2.0.0")


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def updateLabel(self, text):
        self.text_label.text = str(text)


class GpsQuestApp(MDApp):
    def on_start(self):
        print("starting app...")

        self.gps = GpsHelper()

    def build(self):
        self.screen = Builder.load_file('gpsquestapp.kv')

        return self.screen

    def on_pause(self):
        self.gps.stop()
        return True

    def set_current_as_target(self):
        if self.gps.lat and self.gps.lon:
            self.gps.update_target(self.gps.lat, self.gps.lon)
        else:
            self.screen.updateLabel("GPS daten sind noch nicht geladen")


if __name__ == "__main__":
    GpsQuestApp().run()