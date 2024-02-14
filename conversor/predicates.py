from rdflib import Graph, term
from transformer import transformer

class PredicateError(TypeError):
    def __init__(self, error_msg):
        super(TypeError, self).__init__(error_msg)


class Predicates:
    def __init__(self, graph: Graph, pred):
        if not isinstance(pred, term.URIRef):
            raise PredicateError("Subject must be an URI")

        self.prefix, self.url, self.thing = graph.compute_qname(pred)
        if self.thing == "type":
            self.thing = f"{self.prefix}:type"
        self.value = None
        self.isreference = False

    def add_value(self, obj):
        if isinstance(obj, term.Literal) or isinstance(obj, term.URIRef):
            self.isreference = self.isreference or isinstance(obj, term.URIRef)
            value = str(obj) if not isinstance(obj, term.URIRef) else transformer(str(obj))
            if self.value is None:
                self.value = value
            elif type(self.value) is list:
                self.value.append(value)
            else:
                v = self.value
                self.value = [v]
                self.value.append(value)
