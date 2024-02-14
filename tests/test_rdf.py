import json
from unittest import TestCase
from rdflib import term
from conversor.subject_analysis import SubjectAnalysis
from conversor.predicates import PredicateError
from conversor.subjects import SubjectError, Subject
from helpers import get_graph
from config_translator import ConfigTranslator

# from rdflib import namespace
# import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
#                           PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
#                           VOID, XMLNS, XSD


class TestRDFGraph(TestCase):
    """
    Initial testcase for RDF Graph. In helping debug the first example
    """

    def setUp(self) -> None:
        ConfigTranslator("configs/test_config.cfg")


    def test_turtle_1(self):
        '''
        Simple test to check that files can be properly readen

        :return:
        '''
        for file in ['examples/ex012.ttl', 'examples/simple-sample-01.ttl',
                     'examples/ex041.ttl', 'examples/simple-sample-relationship.ttl']:
            g = get_graph(file)

            print(f"Graph g has {len(g)} statemets.")
            # print(g.serialize(format="json-ld"))

            # ttl_thing = g.serialize(format="turtle")

            for subj, pred, obj in g:
                print(f"{subj} | {pred} | {obj}")

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
        g = get_graph("examples/simple-sample-00.ttl")

        for subj, _, _ in g:
            s = Subject(g, subj)
            print(s.subject)
            assert(s.subject == "http://learningsparql.com/ns/addressbook#richard")
            assert(s.short_name == "urn:ngsi-ld:addressbook:richard")
            assert(s.s_type) == "addressbook"


    def test_subject_analysis(self):
        g = get_graph("examples/ex041.ttl")
        sa = SubjectAnalysis(g)

        for a in sa:
            assert(a['type'] == "addressbook")
            assert(a['id'] == "urn:ngsi-ld:addressbook:i0432")
            js = json.dumps(a)
            print(f"curl -iX POST 'http://localhost:1026/ngsi-ld/v1/entities/' \
-H 'Content-Type: application/ld+json' \
--data-raw '{js}'")
            print(js)
            
    def test_sample_relationship(self):
        '''
        Test that ngsi-ld urns are ETSI GS CIM 009 Annex A.3 compliant

            urn:ngsi-ld:EntityTypeName:EntityIdentificationString
        :return:
        '''
        g = get_graph("examples/simple-sample-relationship.ttl")
        sa = SubjectAnalysis(g)

        for a in sa:
            match a['id']:
                case 'urn:ngsi-ld:addressbook:cindy':
                    assert (True)
                case 'urn:ngsi-ld:addressbook:manuel':
                    print("Manuel")
                    assert 'isbossof' in a
                    assert a['isbossof']['object'] == 'urn:ngsi-ld:addressbook:cindy'
                    assert a['isbossof']['type'] == 'Relationship'
                case other:
                    assert(False)

    def do_subject_analysis_parse(self):
        g = get_graph("examples/simple-sample-relationship.ttl")
        sa = SubjectAnalysis(g)
    def test_secuential_processing_speed(self):
        from timeit import timeit
        print(timeit(self.do_subject_analysis_parse, number=2000))

    def test_async_processing_speed(self):
        pass


if __name__ == "__main__":
    import unittest
    import os
    v = os.getcwd()

    unittest.main()
    print(v)

    if True:
        pass
