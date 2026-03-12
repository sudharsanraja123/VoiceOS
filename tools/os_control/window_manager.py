import pyautogui


class WindowManager:

    def close_window(self):

        pyautogui.hotkey("alt", "f4")

        return "Closed current window."

    def switch_window(self):

        pyautogui.hotkey("alt", "tab")

        return "Switched window."