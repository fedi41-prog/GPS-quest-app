
import kivy

from kivy.lang import Builder

from kivy.clock import Clock

from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from gps_helper import GpsHelper

kivy.require("2.0.0")


from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField

import json

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.app = MDApp.get_running_app()
        self.dialog_open = False

    def set_status_color_to_normal(self, dt):
        self.ids.status_label.md_bg_color = (0.2, 0.2, 0.2, 1)

    def show_text_input_dialog(self, key):
        question = self.app.quest[self.app.level]["distances"][key]["text"]
        correct_answers = self.app.quest[self.app.level]["distances"][key]["answers"]
        self.text_field = MDTextField(hint_text="Antwort hier eingeben")

        def on_submit(*args):
            user_input = self.text_field.text.strip().lower()
            self.dialog.dismiss()
            self.app.gps.shown.add(key)
            if user_input in [a.lower() for a in correct_answers]:
                self.ids.status_label.text = "Richtig! neues Ziel gesetzt."
                self.ids.status_label.md_bg_color = (0, 0.6, 0, 1)
                Clock.schedule_once(self.set_status_color_to_normal, 3.0)

                new_level = self.app.quest[self.app.level]["distances"][key]["link"]
                if new_level != "<end>":
                    self.app.level = new_level
                    self.app.gps.update_target()
            else:
                self.ids.status_label.text = "Falsch."
                self.ids.status_label.md_bg_color = (0.8, 0.2, 0.2, 1)
                Clock.schedule_once(self.set_status_color_to_normal, 3.0)

                new_level = self.app.quest[self.app.level]["distances"][key]["wlink"]
                if new_level != "<end>":
                    self.app.level = new_level
                    self.app.gps.update_target()

            self.dialog_open = False


        if not self.dialog_open:
            self.dialog = MDDialog(
                title=question,
                type="custom",
                content_cls=self.text_field,
                buttons=[
                    MDFlatButton(text="Abbrechen", on_release=lambda x: self.dialog.dismiss()),
                    MDFlatButton(text="OK", on_release=on_submit),
                ],
                auto_dismiss=False  # verhindert Schließen durch Tippen außerhalb oder ESC
            )
            self.dialog.open()
            self.dialog_open = True

    def show_multiple_choice_dialog(self, key):
        question = self.app.quest[self.app.level]["distances"][key]["text"]

        def on_button_click(button_instance):
            answer = button_instance.text
            self.dialog.dismiss()
            self.app.gps.shown.add(key)
            if answer in self.app.quest[self.app.level]["distances"][key]["ranswers"]:
                self.ids.status_label.text = "Richtig! neues ziel gesetzt."
                self.ids.status_label.md_bg_color = (0, 0.6, 0, 1)
                Clock.schedule_once(self.set_status_color_to_normal, 3.0)

                new_level = self.app.quest[self.app.level]["distances"][key]["link"]
                if new_level != "<end>":
                    self.app.level = new_level  # <- fix: level speichern im App-Objekt
                    self.app.gps.update_target()
            else:
                self.ids.status_label.text = "Falsch."
                self.ids.status_label.md_bg_color = (0.8, 0.2, 0.2, 1)
                Clock.schedule_once(self.set_status_color_to_normal, 3.0)

                new_level = self.app.quest[self.app.level]["distances"][key]["wlink"]
                if new_level != "<end>":
                    self.app.level = new_level  # <- fix: level speichern im App-Objekt
                    self.app.gps.update_target()


            self.dialog_open = False

        if not self.dialog_open:
            buttons = [
                MDFlatButton(text=a, on_release=on_button_click)
                for a in self.app.quest[self.app.level]["distances"][key]["answers"]
            ]

            self.dialog = MDDialog(
                title=question,
                text="Wähle eine Antwort:",
                buttons=buttons,
                auto_dismiss=False  # verhindert Schließen durch Tippen außerhalb oder ESC
            )
            self.dialog.open()
            self.dialog_open = True

    def show_hint_dialog(self, hint):
        def on_button_click(button_instance):
            self.dialog.dismiss()
            self.dialog_open = False
            self.app.gps.shown.add(key)

        if not self.dialog_open:

            self.dialog = MDDialog(
                title="Tipp: ",
                text=hint,
                buttons = [MDFlatButton(text="schließen", on_release=on_button_click)],
                auto_dismiss=False  # verhindert Schließen durch Tippen außerhalb oder ESC
            )
            self.dialog.open()
            self.dialog_open = True

    def updateMiddleLabel(self, text):
        self.ids.middle_label.text = str(text)

    def updateStatus(self, text):
        self.ids.status_label.text = str(text)


class GpsQuestApp(MDApp):
    def on_start(self):
        print("starting app...")

        self.gps = GpsHelper()

    def build(self):
        self.screen = Builder.load_file('gpsquestapp.kv')

        with open("quest.json", "r") as f:
            self.quest = json.load(f)

        self.level = "start"

        return self.screen

    #def on_pause(self):
    #    self.gps.stop()
    #    return True

    def set_current_as_target(self):
        if self.gps.lat and self.gps.lon:
            self.gps.update_target(self.gps.lat, self.gps.lon)



if __name__ == "__main__":
    GpsQuestApp().run()