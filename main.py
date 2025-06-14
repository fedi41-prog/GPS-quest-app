
import kivy

from kivy.lang import Builder

from kivy.clock import Clock

from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from gps_helper import GpsHelper

from kivy.graphics import Color, RoundedRectangle
from math import sin
import math
import time

kivy.require("2.0.0")

if platform == "android":
    from plyer import vibrator



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
        self.status_color_mode = "rainbow"  # Steuerung: "rainbow", "gray", "green", ...
        self.state = ""
        Clock.schedule_once(self.setup_canvas, 0)

    #border and status label

    def setup_canvas(self, dt):
        self.label = self.ids.status_label
        self.container = self.children[0]

        # Rahmenfarbe (BoxLayout Canvas)
        with self.container.canvas.before:
            self.border_color_instruction = Color(rgba=self.get_current_color())
            self.border_rect = RoundedRectangle(pos=self.container.pos,
                                                size=self.container.size,
                                                radius=[20])

        # Label-Hintergrund
        with self.label.canvas.before:
            self.label_color_instruction = Color(rgba=self.get_current_color())
            self.label_rect = RoundedRectangle(pos=self.label.pos,
                                               size=self.label.size,
                                               radius=[12])

        # Bindings für Größenanpassung
        self.label.bind(pos=self.update_canvas, size=self.update_canvas)
        self.container.bind(pos=self.update_canvas, size=self.update_canvas)

        Clock.schedule_interval(self.update_colors, 0.05)

    def update_canvas(self, *args):
        self.label_rect.pos = self.label.pos
        self.label_rect.size = self.label.size
        self.border_rect.pos = self.container.pos
        self.border_rect.size = self.container.size

    def update_colors(self, dt):
        color = self.get_current_color()
        self.label_color_instruction.rgba = color
        self.border_color_instruction.rgba = color

    def get_current_color(self):
        if self.status_color_mode == "rainbow":
            t = time.time()
            r = 0.6 + 0.2 * math.sin(t)
            g = 0.6 + 0.2 * math.sin(t + 2)
            b = 0.6 + 0.2 * math.sin(t + 4)
            return (r, g, b, 0.9)
        elif self.status_color_mode == "gray":
            return (0.4, 0.4, 0.4, 0.9)
        elif self.status_color_mode == "green":
            return (0.0, 0.7, 0.2, 0.9)
        elif self.status_color_mode == "red":
            return (0.9, 0.1, 0.1, 0.9)
        else:
            return (1, 1, 1, 1)  # fallback (weiß)

    def set_status_color_mode(self, mode: str):
        self.status_color_mode = mode


    #win

    def win(self):
        self.updateStatus("happy happy happy")
        self.updateMiddleLabel("Du hast alle Aufgaben gelöst!")

        # Optional: Hintergrundfarbe ändern
        self.set_status_color_mode("green")  # hellgrün als Hintergrund

        self.state = "win"

        if platform == "android":
            if vibrator.exists():
                vibrator.vibrate(time=1)

        # Optional: autom. Rücksetzung nach 5 Sekunden
        #Clock.schedule_once(self.reset_screen_appearance, 5.0)

    def upgrade_level_wrong(self, key):
        new_level = self.app.quest[self.app.level]["distances"][key]["wlink"]
        if new_level != "<end>":
            self.app.level = new_level
            self.app.gps.update_target()
        else:
            self.win()

        if platform == "android":
            if vibrator.exists():
                vibrator.vibrate(time=0.1)

    def upgrade_level_right(self, key):
        new_level = self.app.quest[self.app.level]["distances"][key]["link"]
        if new_level != "<end>":
            self.app.level = new_level
            self.app.gps.update_target()
        else:
            self.win()

        if platform == "android":
            if vibrator.exists():
                vibrator.vibrate(time=0.1)

    def reset_screen_appearance(self, dt):
        self.set_status_color_mode("rainbow")
        self.state = ""

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
                self.set_status_color_mode("green")
                Clock.schedule_once(self.reset_screen_appearance, 3.0)
                self.state = "right"

                self.upgrade_level_right(key)
            else:
                self.ids.status_label.text = "Falsch. ):"
                self.set_status_color_mode("red")
                Clock.schedule_once(self.reset_screen_appearance, 3.0)
                self.state = "wrong"

                self.upgrade_level_wrong(key)

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
                self.set_status_color_mode("green")
                Clock.schedule_once(self.reset_screen_appearance, 3.0)
                self.state = "right"

                self.upgrade_level_right(key)
            else:
                self.ids.status_label.text = "Falsch."
                self.set_status_color_mode("red")
                Clock.schedule_once(self.reset_screen_appearance, 3.0)
                self.state = "wrong"

                self.upgrade_level_wrong(key)


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

    def show_hint_dialog(self, key):
        hint = self.app.quest[self.app.level]["distances"][key]["text"]

        def on_button_click(button_instance):
            self.dialog.dismiss()
            self.dialog_open = False
            self.app.gps.shown.add(key)

        if not self.dialog_open:
            self.dialog = MDDialog(
                title="Tipp: ",
                text=hint,
                buttons=[MDFlatButton(text="Schließen", on_release=on_button_click)],
                auto_dismiss=False
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