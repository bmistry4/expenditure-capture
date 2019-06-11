# https://stackoverflow.com/questions/49466785/kivy-error-python-2-7-sdl2-import-error
import kivy
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.uix.recycleview import RecycleView
from model import CATEGORY_LIST


kivy.require('1.9.0')

from kivy.app import App


class RecycleViewRow(BoxLayout):
    text = StringProperty()

class TransactionsTable(RecycleView):
    def __init__(self, **kwargs):
        super(TransactionsTable, self).__init__(**kwargs)
        self.data = [{'text': "Button " + str(x), 'id': str(x)} for x in range(12)]


class ViewLayout(FloatLayout):
    pass

class ViewApp(App):
    title = "Expenditure capture"

    def build(self):
        return ViewLayout()


if __name__ == '__main__':
    ViewApp().run()