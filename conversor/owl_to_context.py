from conversor.subject_analysis import SubjectAnalysis
from rdflib import Graph
from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
                           PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
                           VOID, XMLNS, XSD, GEO, BRICK, DCMITYPE, DCAM, WGS
import functools
import json
from helpers import apply_filters

known_namespaces = { str(BRICK), str(DCMITYPE), str(DCAM),
                     str(CSVW),  str(DC),  str(DCAT),  str(DCTERMS),  str(DOAP),  str(FOAF),  str(ODRL2),
                     str(ORG),  str(OWL),  str(PROF),  str(PROV),  str(RDF),  str(RDFS),  str(SDO),
                     str(SH),  str(SKOS),  str(SOSA),  str(SSN),  str(TIME),  str(VOID),  str(XMLNS),  str(XSD),
                     str(GEO), str(WGS),
                     "http://www.w3.org/2002/07/owl#Ontology",
                     }

class Owl2Context:
    """
    Class which interprets an onthology and it will produce data for the @context of the ngsild output.

    """
    @functools.cache
    def __init__(self, g : Graph):
        """
        It will analyze an alrady built Graph
        :param g:
        """
        self.graph = g
        self.namespaces = set()
        self.long_names = {}
        self.short_names = {}
        self.subject_analysis = SubjectAnalysis(g)

        for short_name, long_name in g.namespaces():
            ln = str(long_name)
            sn = str(short_name)
            if ln not in known_namespaces:
                self.namespaces.add(ln)
                self.short_names[ln] = sn
                self.long_names[sn] = str(ln)

    def context(self, filter=None):
        """
        Produces the context from the Onthology, however, it will apply filters if any filter is needed to skip
        certain data which is not required to be represented in the context

        :param filter:
        :return:
        """
        res = {}
        short_names = set()
        for k, v in self.subject_analysis.subjects.items():
            if apply_filters(v, filter) and v.prefix != "":
                try:
                    res[v.prefix] = self.long_names[v.prefix]
                    res[v.thing] = f"{v.prefix}:{v.thing}"
                except KeyError:
                    pass
        self.subject_analysis.set_filter(None)
        return res


if __name__ == "__main__":
    from helpers import get_graph
    g = get_graph("../tests/onthologies/ontology-protege.ttl")
    o = Owl2Context(g)

    filter = {'prefix=="aeros"'}
    context = o.context(filter)
    print(json.dumps(context))
