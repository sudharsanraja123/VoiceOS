import subprocess


def open_app(app):

    try:

        subprocess.Popen(app)

        return f"{app} opened successfully."

    except Exception as e:

        return str(e)
    
def create_file(path):

    with open(path, "w") as f:
        pass

    return f"File created at {path}"

import os


def delete_file(path):

    if os.path.exists(path):

        os.remove(path)

        return "File deleted."

    return "File not found."

def read_file(path):

    if os.path.exists(path):

        with open(path, "r") as f:
            content = f.read()

        return content

    return "File not found."

def write_file(path, content):

    with open(path, "w") as f:
        f.write(content)

    return f"Content written to {path}" 

