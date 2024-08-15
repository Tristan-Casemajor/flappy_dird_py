import time

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.widget import Widget

Builder.load_file("start_screen.kv")






class StartScreen(Widget):
    button_text = StringProperty("Start")
    title_text = StringProperty("Flappy Bird Py")
    current_app = ObjectProperty(None)
    button_width = NumericProperty(dp(100))

    def on_touch_down(self, touch):
        if not self.current_app.game_status:
            time.sleep(0.5)
            self.current_app.game_status = True

        return Widget().on_touch_down(touch) # bien expliquer le retour d'infos du touch


