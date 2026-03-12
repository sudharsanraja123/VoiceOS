import pyperclip


def get_clipboard():

    try:

        return pyperclip.paste()

    except:

        return None