import os

from config_translator import ConfigTranslator
from helpers import encode_url
from requests import post, get, patch
import json
import os

class AlreadyExistException(Exception):
    pass

class NotExistsException(Exception):
    pass

class OrionLD:
    __instance = None
    def __init__(self):
        self.url = ConfigTranslator().get_string("orionld", "url") + "/ngsi-ld/v1/entities/"
        self.headers = {'content-type': 'application/ld+json'}
        self.known_ids = set([])

    @classmethod
    def instance(cls):
        if cls.__instance == None:
            cls.__instance = OrionLD()
        return cls.__instance

    def send(self, payload):
        try:
            if payload['id'] in self.known_ids: # PATCH
                r = self.patch(payload)
                match r.status_code:
                    case 204: # No content - Properly patched!
                        pass
                    case 404: # NOT FOUND => Create!
                        self.known_ids.remove(payload['id'])
                        raise NotExistsException(f"[{id}] does not exists in CB - Retry POST!")
                    case _:
                        print("Status: ", r.status_code)
            else:
                r = self.post(payload)
                match r.status_code:
                    case 201: # Created. Perfect
                        pass
                    case 409: # Conflict. It already exists
                        self.known_ids.add(payload['id'])
                        raise AlreadyExistException(f"[{id}] already exists in CB - Retry PATCH!")
                    case _:
                        print("Status: ", r.status_code)
                self.known_ids.add(payload['id'])
        except ConnectionError:
            # TODO - Log Error
            pass

    def post(self, payload):
        url = self.url
        r = post(url=url, headers=self.headers, data=json.dumps(payload))
        return r

    def patch(self, payload):
        cntx = None
        try:
            cntx = payload.pop("@context")
        except KeyError:
            pass
        id_entity = encode_url(payload['id'])
        headers = {'content-type': 'application/json'}
        url = self.url + id_entity
        try:
            r = patch(url=url, headers=headers, data=json.dumps(payload))
        finally:
            if cntx:
                payload["@context"] = cntx
        return r


if __name__ == "__main__":
    cfg = ConfigTranslator("../config.cfg")
    print(os.getcwd())
    from rdflib import Graph
    from helpers import get_graph
    from conversor.subject_analysis import SubjectAnalysis

    ld = OrionLD()
    files = ["../tests/examples/simple-sample-relationship.ttl", "../tests/examples/containerlab-graph.nt"]
    i=0
    while True:
        g = get_graph(files[i])
        sa = SubjectAnalysis(g)
        i = ( i + 1 ) % 2
        for data in sa:
            try:
                ld.send(data)
            except (NotExistsException, AlreadyExistException) as e:
                # Should retry....
                print(e)
                ld.send(data)
            pass

        # k = input("Enter para seguir")



