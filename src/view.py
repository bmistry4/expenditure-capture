# https://stackoverflow.com/questions/49466785/kivy-error-python-2-7-sdl2-import-error
import kivy
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

import os
from model import *

# kivy.require('1.9.0')

from kivy.app import App


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class RecycleViewRow(BoxLayout):
    text = StringProperty()


class TransactionsTable(RecycleView):
    def __init__(self, **kwargs):
        super(TransactionsTable, self).__init__(**kwargs)
        self.data = [
            {'text': "Button " + str(x),
             'id': str(x)}
            for x in range(12)
        ]


class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    transactions_filepath = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def load(self, path, filename):
        try:
            self.transactions_filepath.text = os.path.join(path, filename[0])

            self.dismiss_popup()


        except IndexError:
            pass


    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()



class ViewApp(App):
    title = "Expenditure capture"

    def build(self):
        return Root()


Factory.register('LoadDialog', cls=LoadDialog)

if __name__ == '__main__':
    ViewApp().run()
