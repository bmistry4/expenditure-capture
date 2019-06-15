# https://stackoverflow.com/questions/49466785/kivy-error-python-2-7-sdl2-import-error

import os

from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout

from model import Model
from table import Table

Config.set("input", "mouse", "mouse, disable_multitouch")
from kivy.app import App
from kivy.core.window import Window
from examples.table.table import Table

model = Model()

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    transactions_filepath = ObjectProperty(None)

    def __init__(self):
        super(Root, self).__init__()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.my_table = Table()
        self.my_table.cols = 2
        self.my_table.label_panel.labels[0].text = "Description" # heading text
        self.my_table.label_panel.labels[1].text = "Category" # heading text

        self.add_widget(self.my_table)


    def dismiss_popup(self):
        self._popup.dismiss()

    def load(self, path, filename):
        try:
            self.transactions_filepath.text = os.path.join(path, filename[0])
            model.process_transactions_file(
                self.transactions_filepath.text)  # create dataframe with transaction details
            model.add_transactions_rows(self.my_table)
            self.dismiss_popup()
        except IndexError:
            pass

    def show_load(self):
        #### TODO - temp
        self.transactions_filepath.text = r'..\data\jan-feb-2018.xlsx'
        model.process_transactions_file(
            self.transactions_filepath.text)  # create dataframe with transaction details
        model.add_transactions_rows(self.my_table)

        #################
        # content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        # self._popup = Popup(title="Load file", content=content,
        #                     size_hint=(0.9, 0.9))
        # self._popup.open()

    def _keyboard_closed(self):
        pass

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """ Method of pressing keyboard  """
        if keycode[0] == 273:  # UP
            print(keycode)
            self.my_table.scroll_view.up()
        if keycode[0] == 274:  # DOWN
            print(keycode)
            self.my_table.scroll_view.down()
        if keycode[0] == 281:  # PageDown
            print(keycode)
            self.my_table.scroll_view.pgdn()
        if keycode[0] == 280:  # PageUp
            print(keycode)
            self.my_table.scroll_view.pgup()
        if keycode[0] == 278:  # Home
            print(keycode)
            self.my_table.scroll_view.home()
        if keycode[0] == 279:  # End
            print(keycode)
            self.my_table.scroll_view.end()

class ViewApp(App):
    title = "Expenditure capture"

    def build(self):
        return Root()


Factory.register('LoadDialog', cls=LoadDialog)

if __name__ == '__main__':
    ViewApp().run()
