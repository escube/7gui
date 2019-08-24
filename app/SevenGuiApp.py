import kivy

kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.textinput import TextInput

Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'resizable', False)
Config.write()

import os
import pyzipper
import time


class SevenGui(FloatLayout):

    def _on_file_drop(self, window, file_path):
        file_path = file_path.decode('utf-8')
        self.set_file(file_path)
        if os.path.exists(file_path):
            if pyzipper.is_zipfile(file_path):
                self.unzip_file(file_path)
            else:
                self.zip_file(file_path)

        else:
            self.set_message("[color=ff3333]Sorry, file does not exists[/color]")

    def set_file(self, path):
        self.file_path = path
        basename = os.path.basename(path)
        self.set_message("[color=00FF6F]file selected : %s[/color]" % basename)

    def reset_file(self):
        self.file_path = None
        self.reset_message()

    def unzip_file(self, file_path):
        dir = os.path.dirname(os.path.abspath(file_path))
        zf = pyzipper.AESZipFile(file_path)
        try:
            zf.extractall(path=dir)
        except RuntimeError as e:
            if "is encrypted" in str(e):
                self.set_file(file_path)
                self.show_password_to_unzip()

    def zip_file(self, file_path):
        self.file_path = file_path
        self.show_password_to_zip()

    def key_down(self, window, keyboard, keycode, text, modifiers):
        if keycode == 41:  # escape
            self.hide_all()

    def show_password_to_zip(self):

        self.tx_password = TextInput(password=True, hint_text='Password', size_hint=(.9, .15),
                                     pos_hint={'center_x': .5, 'center_y': .5},
                                     on_text_validate=self.encrypt,
                                     multiline=False, font_size=32)
        self.add_widget(self.tx_password)
        self.tx_password.focus = True

    def show_password_to_unzip(self):
        self.tx_password = TextInput(password=True, hint_text='Password', size_hint=(.9, .15),
                                     pos_hint={'center_x': .5, 'center_y': .5},
                                     on_text_validate=self.decrypt,
                                     multiline=False, font_size=32)
        self.add_widget(self.tx_password)
        self.tx_password.focus = True

    def set_message(self, message):
        # print(message)
        self.label.text = message

    def reset_message(self):
        # print("[color=00FF6F]Drop your file here[/color]")
        self.label.text = "[color=00FF6F]Drop your file here[/color]"

    def hide_all(self):
        self.remove_widget(self.tx_password)

    def encrypt(self, inputtext):
        self.set_message("[color=E6FF00]Encrypting ...[/color]")
        password = inputtext.text
        base = os.path.basename(self.file_path)

        source = "%s" % (self.file_path)
        os.chdir(os.path.dirname(source))

        destination_file = "%s.zip" % (base)
        i = 1
        while os.path.exists(destination_file):
            destination_file = "%s_%s.zip" % (base, i)
            i += 1



        print("Source:%s" % (base))

        with pyzipper.AESZipFile(destination_file, 'a', compression=pyzipper.ZIP_LZMA) as zf:

            zf.setpassword(str.encode(password))

            zf.setencryption(pyzipper.WZ_AES, nbits=128)

            if os.path.isdir(base):
                self.zipdir(base, zf)
            else:
                zf.write(base)

            zf.close()

        self.hide_all()

    def zipdir(self, path, zf):
        for root, dirs, files in os.walk(path):
            for file in files:
                source = os.path.join(root, file)
                print("Source:%s" % (source))
                zf.write(source)

    def decrypt(self, inputtext):
        self.set_message("[color=E6FF00]Decrypting ...[/color]")
        time.sleep(1)

        password = inputtext.text
        dir = os.path.dirname(os.path.abspath(self.file_path))
        zf = pyzipper.AESZipFile(self.file_path)
        zf.setpassword(str.encode(password))

        try:
            zf.extractall(path=dir)
            self.hide_all()
            self.reset_message()

        except RuntimeError as e:
            if "Bad password" in str(e):
                self.set_message("[color=ff3333]Bad Password, try again[/color]")


class SevenGuiApp(App):

    def build(self):
        sg = SevenGui()
        Window.bind(on_dropfile=sg._on_file_drop)
        Window.bind(on_key_down=sg.key_down)

        Window.size = (300, 300)

        return sg


if __name__ == '__main__':
    SevenGuiApp().run()
