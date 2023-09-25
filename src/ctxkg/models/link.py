from .entity import Entity


class Link:
    def __init__(self, entity_a: Entity, entity_b: Entity):
        self.entity_a: Entity = entity_a
        self.entity_b: Entity = entity_b

    def __repr__(self):
        return f"<Link {self.entity_a} {self.entity_b}>"
