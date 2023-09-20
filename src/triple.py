from src.entity import Entity


class Triple:
    def __init__(self, subject: Entity, relation: str, object: Entity, confidence=1.0):
        self.subject: Entity = subject
        self.relation: str = relation
        self.object: Entity = object
        self.confidence: float = confidence

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
