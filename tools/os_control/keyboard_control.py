import pyautogui


class KeyboardControl:

    def type_text(self, text):

        pyautogui.write(text, interval=0.02)

        return "Typed the requested text."

    def press_key(self, key):

        pyautogui.press(key)

        return f"Pressed {key}"