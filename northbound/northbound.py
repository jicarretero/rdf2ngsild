from northbound.broker_ld import BrokerLD
from northbound.naive import NaiveLD
from northbound.curl_output import CurlOutput
from northbound.print_output import PrintOutput
from northbound.build_single_ngsild import BuildSingleNGSILD
from northbound.exceptions import (
    AlreadyExistException,
    NotExistsException,
    ServerErrorException,
)
import logging

log = logging.getLogger(__name__)


class Northbound(object):
    """
    Instanciates objects as sinks for data read. There are a few - So, depending on the parameters we
    could instanciate any of the sinks for data. The interesting one is the ngisld_broker which sends
    data to a Context Broker and the print one, which outputs data to stdout.
    """

    class __Northbound:
        def __init__(self, args):
            self.args = args
            self.bounds = []
            self.bounds_to_flush = []
            if args.to_null:
                self.bounds.append(NaiveLD())
            if args.to_ngsild_broker:
                self.bounds.append(BrokerLD(args))
            if args.curl:
                self.bounds.append(CurlOutput(args))
            if args.print:
                self.bounds.append(PrintOutput(args))
            if args.single_ngsild:
                single_ngisld = BuildSingleNGSILD(args)
                self.bounds.append(single_ngisld)
                self.bounds_to_flush.append(single_ngisld)

        def send(self, payload):
            """
            Sends data to the Northbounds defined in the args

            :param payload:
            :return:
            """
            for bound in self.bounds:
                try:
                    bound.send(payload)
                except (
                    AlreadyExistException,
                    NotExistsException,
                    ServerErrorException,
                ):
                    try:
                        bound.send(payload)
                    except (
                        AlreadyExistException,
                        NotExistsException,
                        ServerErrorException,
                    ) as e:
                        log.error(f"Reprocessing exception: {e}")

    instance = None

    def __new__(cls, args=None):
        if Northbound.instance is None:
            Northbound.instance = Northbound.__Northbound(args)
        return cls.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)


if __name__ == "__main__":
    try:
        raise NotExistsException("No existe la excepcion")
    except NotExistsException as e:
        print(f"Esto es un error {e}")
        log.error(f"Error, pero en log {e}")
