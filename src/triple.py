from typing import TYPE_CHECKING

from .entity import Entity


class Triple:
    def __init__(self, subject: Entity = None, relation: str = None, object: Entity = None, confidence=1.0):
        self.subject: Entity = subject
        self.relation: str = relation
        self.object: Entity = object
        self.confidence: float = confidence

    @staticmethod
    def header(filename):
        return f"# {filename}\nconfidence;subject;relation;object;subject_id;object_id\n" 

    @staticmethod
    def build_derived_triple(main_e: Entity, relation: str, derived_e: Entity):
        if relation in ["acl", "amod", "appos", "obl:npmod"]:
            return Triple(main_e, "is", derived_e)
        if relation in ["advmod", "advmod:emph", "advmod:lmod", "csubj", "csubj:pass", 
                        "goeswith", "nsubj", "nsubj:pass", "obj", "obl", "obl:arg",
                        "obl:lmod", "obl:tmod", "xcomp"]:
            return Triple(main_e, "at", derived_e)
        if relation in ["compound", "nmod"]:
            return Triple(main_e, "of", derived_e)
        if relation in ["conj"]:
            return Triple(main_e, "and", derived_e)
        if relation in ["nmod:poss", "nmod:tmod"]:
            return Triple(derived_e, "has", main_e)
        if relation in ["nummod", "nummod:gov"]:
            return Triple(main_e, "amount to", derived_e)
        if relation in ["obl:agent"]:
            return Triple(main_e, "by", derived_e)
        if relation in ["vocative"]:
            return Triple(derived_e, "referenced by", main_e)
        if relation in ["acl:relcl", "advcl", "aux", "aux:pass", "case", "cc", "cc:preconj",
                        "ccomp", "clf", "compound:lvc", "compound:prt", "compound:redup",
                        "compound:svc", "cop", "dep", "det", "det:numgov", "det:nummod",
                        "det:poss", "discourse", "dislocated", "expl", "expl:impers",
                        "expl:pass", "expl:pv", "fixed", "flat", "flat:foreign", "flat:name",
                        "iobj", "list", "mark", "orphan", "parataxis", "punct", "reparandum", "root"]:
            return Triple(main_e, relation, derived_e)
        return Triple(main_e, relation, derived_e)

    def as_csv_row(self):
        return f"{self.confidence};\"{self.subject.text}\";\"{self.relation}\";\"{self.object.text}\";\"{self.subject.dynamic_id()}\";\"{self.object.dynamic_id()}\""

    def entities(self):
        return (self.subject, self.object)

    def to_text(self):
        return f"{self.subject.text} {self.relation} {self.object.text}"

    def includes_entity(self, entity):
        return self.subject is entity or self.object is entity

    def replace_entity(self, original: Entity, replacement: Entity):
        if original is self.subject:
            self.subject = replacement
        if original is self.object:
            self.object = replacement

    def __eq__(self, o: "Triple"):
        return self.subject is o.subject and self.relation == o.relation and self.object is o.object

    def __repr__(self):
        return f"<Triple {self.confidence} {self.subject} {self.relation} {self.object}>"