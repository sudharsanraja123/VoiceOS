import os
import requests
from core.config import config
from core.logger import logger


class ModelDownloader:

    def download_file(self, url, path):

        logger.info(f"Downloading model from {url}")

        r = requests.get(url, stream=True)

        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info("Download complete.")