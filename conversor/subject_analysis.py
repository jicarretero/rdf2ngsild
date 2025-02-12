from rdflib import Graph, URIRef
from  transformer import unquote
from conversor.subjects import Subject, BNodeFoundException
from config_translator import ConfigTranslator


class SubjectAnalysis:
    """
    Class for analyzing rdf Graph.

    The __init__ method will get a Graph, so it can build a representation of the Graph so that
    it can be later translated to a ngsi-ld format.

    """

    def __init__(self, graph: Graph):
        """
        Given a Graph as a parameter, this init method triggers the building of a NDSI-LD ready representation.

        :param graph:
        """
        self.graph = graph
        self.filter = set()
        self.subjects = {}
        self.extra_context = {}

        for subj, pred, obj in graph:
            subj = URIRef(unquote(str(subj))) if type(subj) == URIRef else subj
            pred = URIRef(unquote(str(pred))) if type(pred) == URIRef else pred
            obj = URIRef(unquote(str(obj))) if type(obj) == URIRef else obj
            self.set_subject_data(subj, pred, obj)

        # TODO - This context should be produced as parameter.
        self.context = ConfigTranslator().get_list("default", "context")

    def add_context(self, context):
        """
        Adds something to the context. Then, this added context will be inserted in the final ngsi-ld context.

        :param context:
        :return:
        """
        if context is not None:
            self.extra_context.update(context)

    def set_subject_data(self, subj, pred, obj):
        """
        Given a RDF triple, this method will recieve the Subject, the Predicate and the Object. With these parameters
        it will build an internal representation of an entity (basically a subject) and it will be adding new
        relationships or attibutes (predicates and objects) to it.

        :param subj:
        :param pred:
        :param obj:
        :return:
        """
        s_id = str(subj)
        # print(f"{str(subj)} | {str(pred)} | {str(obj)}")
        if s_id not in self.subjects:
            self.subjects[s_id] = Subject(self.graph, subj, self)

        try:
            uri = str(subj)
            self.subjects[s_id].push_data(pred, obj)
        except BNodeFoundException as bne:
            bnodeid = str(obj)
            if bnodeid not in self.subjects:
                self.subjects[bnodeid] = Subject(self.graph, obj)
            self.subjects[s_id].push_bnode(pred, self.subjects[bnodeid])

    def set_filter(self, filter):
        """
        Adds a filter, to change the json-ld object produced by the entity.

        :param filter:
        :return:
        """
        if filter is None:
            self.filter = set()
        else:
            self.filter.add(filter)

    def apply_filters(self, subject: Subject):
        """
        Applies the filters to the subject so it can skip or prevent producing some output

        :param subject:
        :return:
        """
        r = True
        if len(self.filter) > 0:
            for f in self.filter:
                prefix = subject.prefix
                r = r and eval(f)
                if r == False:
                    break
        return r

    def __iter__(self):
        """
        Iterates accross the Subjects and produces a ngsi-ld object for each entity not filtered.

        :return:
        """
        for k, v in self.subjects.items():
            if v.is_bnode or not self.apply_filters(v):
                continue
            s = {}
            # s['id'] = k
            s['id'] = v.short_name
            s['type'] = str(v.s_type)

            for pr_k, pr_v, is_r in v:
                t, o = ("Relationship", "object") if is_r else (
                    "Property", "value")
                if "isGeo" in pr_v:
                    t="GeoProperty"
                    pr_v.pop("isGeo")
                s[pr_k] = {"type": t, o: pr_v}

            s['@context'] = list(self.context)
            if len(self.extra_context) > 0:
                s['@context'].append(self.extra_context)

            yield s

    def prefixes(self):
        """
        Kind of internal method which processes blank nodes related to a subject and merges them all in a struct as
        an attribute of the Entity.

        :return: Object as an Attribute of an Entity
        """
        r = set()
        for k, v in self.subjects.items():
            if v.is_bnode:
                continue
            r.add(v.prefix)
        return r
