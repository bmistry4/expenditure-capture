# https://stackoverflow.com/questions/49466785/kivy-error-python-2-7-sdl2-import-error

# C:\Users\Bhumika\Documents\Coding Projects\expenditure-capture\data\jan-feb-2018.xlsx

import os

from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView

from model import Model
from table import Table

from kivy.config import Config

Config.set("input", "mouse", "mouse, disable_multitouch")
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from examples.table.table import Table
from kivy.uix.spinner import Spinner

model = Model()

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


# class RecycleViewRow(BoxLayout):
#     text = StringProperty()
#
#
# class TransactionsTable(RecycleView):
#     def __init__(self, **kwargs):
#         super(TransactionsTable, self).__init__(**kwargs)
#         self.data = [
#             {'text': "Button " + str(x),
#              'id': str(x)}
#             for x in range(5)
#         ]


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

    def on_click(self):
        self.my_table.grid.cells[1][0].color_widget = [1, 0, 1, 0.6]
        for row in self.my_table.grid._cells:
            print(row[0].text, row[1].text)



class ViewApp(App):
    title = "Expenditure capture"

    def build(self):
        return Root()


Factory.register('LoadDialog', cls=LoadDialog)

if __name__ == '__main__':
    ViewApp().run()
