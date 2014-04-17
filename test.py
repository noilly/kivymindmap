from kivy.app import App
from kivy.lang import Builder

class MainApp(App):

    def build(self):
        return Builder.load_string('''
#:import Factory kivy.factory.Factory

FloatLayout
    Button
        pos_hint: {'center': (.5, .5)}
        size_hint: .5, .5
    Button
        pos_hint: {'center': (.4, .4)}
        size_hint: .5, .5
        on_release:
            root.add_widget(\
            Factory.Image(size_hint=(.5, .5),\
            pos_hint={'center':(.3, .5)}),\
            index=1)
''')

MainApp().run()