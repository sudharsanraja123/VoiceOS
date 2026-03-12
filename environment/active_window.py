import pygetwindow as gw


def get_active_window():

    try:

        window = gw.getActiveWindow()

        if window:
            return window.title

    except:
        pass

    return None