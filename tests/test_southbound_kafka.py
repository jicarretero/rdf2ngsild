import time
import unittest
from config_translator import ConfigTranslator
from southbound.kafka_writer import KafkaWriter
from southbound.kafka_reader import KafkaReader
from rdflib import Graph
from conversor.subject_analysis import SubjectAnalysis

class TestSouthboundKafka(unittest.TestCase):
    def setUp(self) -> None:
        ConfigTranslator("configs/test_config_nameonly.cfg")

    def thread_writer(self):
        print("EN THREAD WRITER!")
        with open("examples/containerlab-graph.nt", "r") as f:
            data = f.read()
        kw = KafkaWriter().produce_message(data)

    def test_kafka(self):
        r = KafkaReader()
        self.thread_writer()
        time.sleep(0.3)

        print("EN THREAD Reader!")
        msg = r.consume_one()
        r.commit()
        assert(msg is not None)

        g = Graph()
        g.parse(data=msg)

        sa = SubjectAnalysis(g)
        for a in sa:
            match a['id']:
                case 'srl1_e1-1-srl2_e1-1':
                    assert a['type'] == 'Link'
                    assert a['connectsNode']['type'] == 'Relationship'
                    assert 'clab-srlinux-openconfig-02-srl1' in a['connectsNode']['object']
                    assert 'clab-srlinux-openconfig-02-srl2' in a['connectsNode']['object']
                    assert a['linkIdentifier']['type'] == 'Property'
                    assert a['linkIdentifier']['value'] == 'srl1_e1-1-srl2_e1-1'
                case 'srlinux-openconfig-02':
                    assert a['type'] == 'Network'
                case 'clab-srlinux-openconfig-02-srl2':
                    assert a['type'] == 'Node'
                case 'clab-srlinux-openconfig-02-srl1':
                    assert a['type'] == 'Node'
                case 'clab-srlinux-openconfig-02-srl2':
                    assert a['type'] == 'Node'
                case 'srl1-e1-1':
                    assert a['type'] == 'Interface'
                case 'srl2-e1-1':
                    assert a['type'] == 'Interface'
                case other:
                    assert True


if __name__ == '__main__':
    print("Estoy en la puta clase que quiero estar!")
    unittest.main()