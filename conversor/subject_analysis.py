from rdflib import Graph

from conversor.subjects import Subject, BNodeFoundException
import json

class SubjectAnalysis:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.filter = set()
        self.subjects = {}
        self.extra_context = { }

        for subj, pred, obj in graph:
            self.set_subject_data(subj, pred, obj)

        self.context = {
            "https://fiware.github.io/data-models/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        }

    def add_context(self, context):
        if context is not None:
            self.extra_context.update(context)

    def set_subject_data(self, subj, pred, obj):
        s_id = str(subj)
        # print(f"{str(subj)} | {str(pred)} | {str(obj)}")
        if s_id not in self.subjects:
            self.subjects[s_id] = Subject(self.graph, subj)

        try:
            self.subjects[s_id].push_data(pred, obj)
        except BNodeFoundException as bne:
            bnodeid = str(obj)
            if bnodeid not in self.subjects:
                self.subjects[bnodeid] = Subject(self.graph, obj)
            self.subjects[s_id].push_bnode(pred, self.subjects[bnodeid])

    def set_filter(self, filter):
        if filter is None:
            self.filter = set()
        else:
            self.filter.add(filter)

    def apply_filters(self, subject: Subject):
        r = True
        if len(self.filter) > 0:
            for f in self.filter:
                prefix = subject.prefix
                r = r and eval(f)
                if r == False:
                    break
        return r

    def __iter__(self):
        for k, v in self.subjects.items():
            if v.is_bnode or not self.apply_filters(v):
                continue
            s = {}
            s['id'] = k
            s['type'] = str(v.url)  # .removesuffix("#")

            for pr_k, pr_v, is_r in v:
                t, o = ("Relationship", "object") if is_r else ("Property", "value")
                s[pr_k] = {"type": t, o: pr_v}

            s['@context'] = list(self.context)
            if len(self.extra_context) > 0:
                s['@context'].append(self.extra_context)

            yield s

    def prefixes(self):
        r = set()
        for k, v in self.subjects.items():
            if v.is_bnode:
                continue
            r.add(v.prefix)
        return r
