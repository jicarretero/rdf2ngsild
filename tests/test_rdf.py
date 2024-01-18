import json
from unittest import TestCase
from rdflib import term
from conversor.subject_analysis import SubjectAnalysis
from conversor.predicates import PredicateError
from conversor.subjects import SubjectError, Subject
from helpers import get_graph

# from rdflib import namespace
# import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
#                           PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
#                           VOID, XMLNS, XSD


class TestRDFGraph(TestCase):
    """
    Initial testcase for RDF Graph. In helping debug the first example
    """

    def setUp(self) -> None:
        pass

    def test_turtle_1(self):
        g = get_graph("examples/ex041.ttl")

        print(f"Graph g has {len(g)} statemets.")
        # print(g.serialize(format="json-ld"))

        ttl_thing = g.serialize(format="turtle")

        for a in g.namespaces():
            print(a)

        for subj, pred, obj in g:
            print(f"{subj} | {pred} | {obj}")

    def test_namespaces(self) -> None:
        g = get_graph("examples/ex041.ttl")
        for subj, pred, _ in g:
            # print(f"{type(subj)} | {type(pred)} | {type(obj)}")
            if isinstance(subj, term.URIRef):
                prefix, uri, thing = g.compute_qname(subj)
                print(prefix, uri, thing)
            if isinstance(pred, term.URIRef):
                prefix, uri, thing = g.compute_qname(pred)
                print(str(pred))
                print(prefix, uri, thing)
                print("    ", term.URIRef)

    def test_exceptions(self):
        a = PredicateError("Hola mundo")
        try:
            raise a
        except PredicateError as pe:
            assert str(pe) == "Hola mundo"

        a = SubjectError("Hola mundo")
        try:
            raise a
        except SubjectError as pe:
            assert str(pe) == "Hola mundo"

    def test_subject(self):
        g = get_graph("onthologies/ontology-protege.ttl")

        for subj, _, _ in g:
            s = Subject(g, subj)
            if not s.is_bnode:
                print(s)


    def test_subject_analysis(self):
        g = get_graph("examples/ex041.ttl")
        sa = SubjectAnalysis(g)
        for subj, pred, obj in g:
            sa.set_subject_data(subj, pred, obj)

        for a in sa:
            js = json.dumps(a)
            print(f"curl -iX POST 'http://localhost:1026/ngsi-ld/v1/entities/' \
-H 'Content-Type: application/ld+json' \
--data-raw '{js}'")
            print(js)


if __name__ == "__main__":
    import unittest
    import os
    v = os.getcwd()

    unittest.main()
    print(v)

    if True:
        pass
