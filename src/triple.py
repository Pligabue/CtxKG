from src.entity import Entity


class Triple:
    def __init__(self, subject: Entity = None, relation: str = None, object: Entity = None, confidence=1.0):
        self.subject = subject
        self.relation = relation
        self.object = object
        self.confidence = confidence

    def to_text(self):
        return f"{self.subject.text} {self.relation} {self.object.text}"

    def __repr__(self):
        return f"<Triple {self.confidence} {self.subject} {self.relation} {self.object}>"