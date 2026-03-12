import subprocess
import platform


class AppLauncher:

    def open_app(self, app_name):

        system = platform.system()

        if system == "Windows":
            subprocess.Popen(app_name)

        elif system == "Darwin":
            subprocess.Popen(["open", "-a", app_name])

        elif system == "Linux":
            subprocess.Popen([app_name])

        return f"Opening {app_name}"