from transformer import encode_url
import json

class PrintOutput:
    def __init__(self, args):
        self.args = args

    def send(self, payload):
        output = json.dumps(payload)
        if self.args.get_curl:
            url = encode_url(payload['id'])
            output = output.join("\n").join(f"curl 'http://localhost:1026/ngsi-ld/v1/entities/{url}'")
        print(output)
