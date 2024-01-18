import unittest
from conversor.subject_analysis import SubjectAnalysis
from helpers import get_graph
import json

class TestRelationships(unittest.TestCase):

    def test_simple_relationship(self):
        g = get_graph("examples/simple-sample-relationship.ttl")
        sa = SubjectAnalysis(g)

        for subj, pred, obj in g:
            sa.set_subject_data(subj, pred, obj)
        for a in sa:
            js = json.dumps(a)
            print(f"curl -iX POST 'http://localhost:1026/ngsi-ld/v1/entities/' \
-H 'Content-Type: application/ld+json' \
--data-raw '{js}'")
            print(js)

if __name__ == '__main__':
    unittest.main()
