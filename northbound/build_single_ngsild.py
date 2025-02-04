from transformer import encode_url
import json

class BuildSingleNGSILD:
    def __init__(self, args):
        self.args = args
        self.full_data = []

    def send(self, payload):
        self.full_data.append(payload)

    def data(self):
        return self.full_data

    def json_data(self):
        return json.dumps(self.full_data)
