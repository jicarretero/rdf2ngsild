from urllib.parse import unquote

from rdflib import Graph, term

from config_translator import ConfigTranslator
from dateutil import parser
import pytz
from common.tzinfos import whois_timezone_info
from datetime import timezone
from conversor.predicates import PredicateError, Predicates
from transformer import transformer, type_transformer, retype

class BNodeFoundException(TypeError):
    def __init__(self, error_msg):
        super(TypeError, self).__init__(error_msg)


class SubjectError(TypeError):
    def __init__(self, error_msg):
        super(TypeError, self).__init__(error_msg)


class Subject:
    """
    Class which takes a Subject from a Graph and builds the Entity structure
    """
    def __init__(self, graph: Graph, subject, analysis=None):
        """

        :param graph: Graph to be analyzed
        :param subject:  Subject in the graph
        """
        self.graph = graph
        self.predicates = {}
        self.bnodes = {}
        self.bnode = None
        self.is_bnode = False
        self.subject_object = subject
        self.subject = str(subject)
        self.short_name = transformer(self.subject)
        self.uri = str(subject)
        self.analysis = analysis

        if isinstance(subject, term.URIRef):
            try:
                if str(subject).startswith('https://rdflib.github.io/.well-known/genid/rdflib/'):
                    self.is_bnode = True
                self.prefix, self.url, self.thing = graph.compute_qname(
                    subject)
                self.url = unquote(self.url)
                self.s_type = type_transformer(self.url)
            except ValueError:
                # This is likely to be an onthology
                self.url = str(subject)
                self.prefix = ""
                self.thing = ""
                self.s_type = self.url
        elif isinstance(subject, term.BNode):
            self.prefix = "_"
            self.url = "_"
            self.thing = str(subject)
            self.is_bnode = True
        else:
            raise SubjectError("Subject must be an URI")

    def stodate(self, value):
        """
            Converts a date in string format to UTC date using
        """
        dt = parser.parse(value, tzinfos=whois_timezone_info)
        dt = dt.astimezone(pytz.UTC)
        return dt.replace(tzinfo=timezone.utc).isoformat()

    def put_bnode(self, pred_name, bnode_id):
        self.bnodes[bnode_id] = pred_name

    def push_data(self, pred, obj):
        """
        Given a predicate and an object in a triple with this object as subject, it will add the information read from
        the predicate and the object of the RDF triple to this object.

        :param pred: Predicate found in analysis
        :param obj:  Object related to the predicate
        :return: object id if object is a bnode.
        """
        if not isinstance(pred, term.URIRef):
            raise PredicateError("Predicate must be URIRef")

        if isinstance(obj, term.BNode):
            raise BNodeFoundException(str(obj))

        obj_id = str(obj)

        if obj_id.startswith('https://rdflib.github.io/.well-known/genid/rdflib/'):
            self.put_bnode(str(obj), str(pred))
        else:
            obj_id = None

        p_id = str(pred)
        if p_id not in self.predicates:
            pr = Predicates(self.graph, pred)
            if pr.thing == 'rdf:type' or pr.thing == 'a':
                try:
                    self.s_type = retype(str(obj), 'a', self.s_type)
                except:
                    pass
                return obj_id
            else:
                self.predicates[p_id] = pr
        self.predicates[p_id].add_value(obj)
        return obj_id

    def push_bnode(self, pred, bnode):
        """
        When the bnode is completed (some kind of structure as the value of this Subject), this will be appended to
        as an attribute.

        :param pred:
        :param bnode:
        :return:
        """
        self.bnode = bnode
        self.bnod_predicate = Predicates(self.graph, pred)

    def __iter__(self):
        """
        Iterator yielding, for every predicate related to this Subject the data related to it as Entity or Relationship.
        It will be basically used by the SubjectAnalysis class

        :return:
        """
        for k, v in self.predicates.items():
            format = ConfigTranslator.instance.get_string("predicates", "format")

            match format:
                case 'long':
                    thing = f"{v.url}{v.thing}"
                case 'prefix':
                    thing = f"{v.prefix}:{v.thing}"
                case _:
                    thing = v.thing

            if v.isBnodeData:
                u = v.url
                su = str(v.url) + v.thing
                subject_bnode = self.bnodes[su]
                bnode_object = self.analysis.subjects[subject_bnode]

                yld_value = {}
                for key, value, is_r in bnode_object:
                    if k == "http://uri.etsi.org/ngsi-ld/location":
                        try:
                            value = [float(value[0]), float(value[1])]
                        except ValueError:
                            pass
                        value = {"type":"Point", "coordinates": value, "isGeo": True}
                        yld_value = value
                    else:
                        yld_value[key] = value

                yield thing, yld_value, False
            else:
                yield thing, v.value, v.isreference


    def __str__(self):
        """
        String representation of the subject

        :return: a representation of the object as a string
        """
        return f"{self.prefix} | {self.thing} | {self.url}"
