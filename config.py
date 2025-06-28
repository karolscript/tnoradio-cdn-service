import os
from dotenv import load_dotenv
load_dotenv(".env")

class config:
    def __init__(self):
        self.get = self.get

    def get(self, key):
        return os.environ.get(key)