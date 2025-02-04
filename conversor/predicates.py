from rdflib import Graph, term
from transformer import transformer

class PredicateError(TypeError):
    def __init__(self, error_msg):
        super(TypeError, self).__init__(error_msg)


class Predicates:
    """
    Class representing predicates for the Subjects. Given a graph and a predicate, this class serves as an internal
    representation of the predicate.
    """
    def __init__(self, graph: Graph, pred):
        """
        This will build the predicates and will hold its values

        :param graph:
        :param pred:
        """
        if not isinstance(pred, term.URIRef):
            raise PredicateError("Subject must be an URI")

        self.prefix, self.url, self.thing = graph.compute_qname(pred)

        if self.thing == "type":
            self.thing = f"{self.prefix}:type"
        self.value = None
        self.isreference = False
        self.isBnodeData = False


    def add_value(self, obj):
        """
        The predicate will contain one or more values, so this predicate will held the values.

        :param obj:
        :return:
        """
        if isinstance(obj, term.Literal) or isinstance(obj, term.URIRef):
            self.isBnodeData = str(obj).startswith('https://rdflib.github.io/.well-known/genid/rdflib/')
            self.isreference = (self.isreference or isinstance(obj, term.URIRef)) and not self.isBnodeData
            value = str(obj) if not isinstance(obj, term.URIRef) else transformer(str(obj))
            if self.value is None:
                self.value = value
            elif type(self.value) is list:
                self.value.append(value)
            else:
                v = self.value
                self.value = [v]
                self.value.append(value)
