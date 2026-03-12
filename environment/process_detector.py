import psutil


def list_running_apps():

    apps = []

    for proc in psutil.process_iter(['name']):

        try:
            apps.append(proc.info['name'])

        except:
            pass

    return apps