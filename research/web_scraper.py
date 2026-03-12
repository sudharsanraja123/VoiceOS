import requests


def fetch_page(url):

    try:

        r = requests.get(url, timeout=10)

        return r.text

    except:

        return None