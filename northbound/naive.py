import os

from config_translator import ConfigTranslator
from transformer import encode_url
from requests import post, get, patch, Session
import json
import os
import logging
from northbound.exceptions import AlreadyExistException, NotExistsException

log = logging.getLogger(__name__)


class NaiveLD:
    """
    Class connecting and sending data to a ngsi-ld Broker.
    """
    __instance = None

    def __init__(self):
        """
        Sets the configuration according to the configuration file
        """
        self.url = ConfigTranslator().get_string(
            "orionld", "url") + "/ngsi-ld/v1/entities/"
        self.headers = {'content-type': 'application/ld+json'}
        self.known_ids = set([])
        self.session = Session()

    @classmethod
    def instance(cls):
        """
        It gets an instance (instead of building an object each time) to be used (if required) as Singleton.

        :return:
        """
        if cls.__instance == None:
            cls.__instance = NaiveLD()
        return cls.__instance

    def send(self, payload):
        """
        Sends data to the Orion-ld. This can be sent in a POST or in a PATCH, depending our knonwledge on the entity.
        It can throw any of AlreadyExistsException and NotExistsException. In both cases, it should be retried.

        :param payload: Data to be sent to a NGSILD Context broker
        :return:
        """
        try:
            if payload['id'] in self.known_ids:  # PATCH
                r = self.patch(payload)
                match r:
                    case 204:  # No content - Properly patched!
                        pass
                    case 404:  # NOT FOUND => Create!
                        self.known_ids.remove(payload['id'])
                        raise NotExistsException(
                            f"[{id}] does not exists in CB - Retry POST!")
                    case _:
                        print("Status: ", r)
            else:
                r = self.post(payload)
                match r:
                    case 201:  # Created. Perfect
                        pass
                    case 409:  # Conflict. It already exists
                        self.known_ids.add(payload['id'])
                        raise AlreadyExistException(
                            f"[{id}] already exists in CB - Retry PATCH!")
                    case _:
                        print("Status: ", r)
                self.known_ids.add(payload['id'])
        except ConnectionError:
            # TODO - Log Error
            pass

    def post(self, payload):
        """
        Posts data to a Context Broker (the entity is not known to exist),

        :param payload:
        :return:
        """
        url = self.url
        log.info("POST %d -- %s" % (201, payload['id']))
        return 201

    def patch(self, payload):
        """
        Patch data of an entity in a Context Broker (the entity is supposed to exist).

        :param payload:
        :return:
        """
        cntx = None
        try:
            cntx = payload.pop("@context")
        except KeyError:
            pass
        id_entity = encode_url(payload['id'])
        headers = {'content-type': 'application/json'}
        url = self.url + id_entity
        try:
            log.info("PATCH %d -- %s" % (204, payload['id']))
        finally:
            if cntx:
                payload["@context"] = cntx
        return 204


if __name__ == "__main__":
    cfg = ConfigTranslator("../config.cfg")
    print(os.getcwd())
    from rdflib import Graph
    from helpers import get_graph
    from conversor.subject_analysis import SubjectAnalysis

    ld = NaiveLD()
    files = ["../tests/examples/simple-sample-relationship.ttl",
             "../tests/examples/containerlab-graph.nt"]
    i = 0
    while True:
        g = get_graph(files[i])
        sa = SubjectAnalysis(g)
        i = (i + 1) % 2
        for data in sa:
            try:
                ld.send(data)
            except (NotExistsException, AlreadyExistException) as e:
                # Should retry....
                print(e)
                ld.send(data)
            pass

        # k = input("Enter para seguir")
