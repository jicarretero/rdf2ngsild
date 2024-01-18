from rdflib import Graph, term

from conversor.predicates import PredicateError, Predicates

class BNodeFoundException(TypeError):
    def __init__(self, error_msg):
        super(TypeError, self).__init__(error_msg)

class SubjectError(TypeError):
    def __init__(self, error_msg):
        super(TypeError, self).__init__(error_msg)


class Subject:
    def __init__(self, graph: Graph, subject):
        self.graph = graph
        self.predicates = {}
        self.bnode = None
        self.bnod_predicate = None
        self.is_bnode = False
        self.subject = subject
        self.uri = str(subject)
        if isinstance(subject, term.URIRef):
            try:
                self.prefix, self.url, self.thing = graph.compute_qname(subject)
            except ValueError:
                # This is likely to be an onthology
                self.url = str(subject)
                self.prefix = ""
                self.thing = ""
        elif isinstance(subject, term.BNode):
            self.prefix="_"
            self.url="_"
            self.thing = str(subject)
            self.is_bnode = True
        else:
            raise SubjectError("Subject must be an URI")

    def push_data(self, pred, obj):
        if not isinstance(pred, term.URIRef):
            raise PredicateError("Predicate must be URIRef")
        if isinstance(obj, term.URIRef):
            pass
        elif isinstance(obj, term.BNode):
            raise BNodeFoundException(str(obj))
        p_id = str(pred)
        if p_id not in self.predicates:
            self.predicates[p_id] = Predicates(self.graph, pred)
        self.predicates[p_id].add_value(obj)

    def push_bnode(self, pred, bnode):
        self.bnode = bnode
        self.bnod_predicate = Predicates(self.graph, pred)

    def __iter__(self):
        for _, v in self.predicates.items():
            yield v.thing, v.value, v.isreference

        if self.bnode is not None:
            r = {}
            is_reference = None
            for k, v, is_reference in self.bnode:
                r[k] = v
            yield self.bnod_predicate.thing, r, is_reference


        #if self.bnode is not None:
        #    for k, v in self.bnode:
        #        print(k)
        #        print(v)

    def __str__(self):
        return f"{self.prefix} | {self.thing} | {self.url}"



