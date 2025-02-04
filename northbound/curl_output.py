from transformer import encode_url
import json
class CurlOutput:
    def __init__(self, args):
        self.args = args

    def send(self, payload):
        js = json.dumps(payload)
        output = f"curl -iX POST 'http://localhost:1026/ngsi-ld/v1/entities/' \
        -H 'Content-Type: application/ld+json' \
        --data-raw '{js}'"
        if self.args.get_curl:
            url = encode_url(payload['id'])
            output = output.join("\n").join(f"curl 'http://localhost:1026/ngsi-ld/v1/entities/{url}'")
        print(output)