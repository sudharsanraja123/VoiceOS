from tools.os_control.app_launcher import AppLauncher
from tools.os_control.keyboard_control import KeyboardControl
from tools.os_control.window_manager import WindowManager
from tools.os_control.clipboard_tool import ClipboardTool


class OSToolRouter:

    def __init__(self):

        self.app = AppLauncher()
        self.keyboard = KeyboardControl()
        self.window = WindowManager()
        self.clipboard = ClipboardTool()

    def execute(self, tool, args):

        if tool == "open_app":
            return self.app.open_app(args["app"])

        if tool == "type_text":
            return self.keyboard.type_text(args["text"])

        if tool == "press_key":
            return self.keyboard.press_key(args["key"])

        if tool == "close_window":
            return self.window.close_window()

        if tool == "switch_window":
            return self.window.switch_window()

        if tool == "set_clipboard":
            return self.clipboard.set_clipboard(args["text"])

        return "Unknown OS action."