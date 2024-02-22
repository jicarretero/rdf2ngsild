from northbound.broker_ld import BrokerLD
from northbound.naive import NaiveLD
from northbound.curl_output import CurlOutput
from northbound.print_output import PrintOutput
from northbound.exceptions import AlreadyExistException, NotExistsException, ServerErrorException


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
            if args.to_null:
                self.bounds.append(NaiveLD())
            if args.to_ngsild_broker:
                self.bounds.append(BrokerLD(args))
            if args.curl:
                self.bounds.append(CurlOutput(args))
            if args.print:
                self.bounds.append(PrintOutput(args))

        def send(self, payload):
            """
            Sends data to the Northbounds defined in the args

            :param payload:
            :return:
            """
            for bound in self.bounds:
                try:
                    bound.send(payload)
                except (AlreadyExistException, NotExistsException, ServerErrorException):
                    bound.send(payload)

    instance = None

    def __new__(cls, args=None):
        if Northbound.instance is None:
            Northbound.instance = Northbound.__Northbound(args)
        return cls.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)
