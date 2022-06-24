from uuid import UUID
import tensorflow as tf
import re

from .token_tree import TokenTree


class Entity:
    expected_noun_tags = ["NN", "NNP", "NNS", "NNPS"]
    trimmable_tags = ["IN"]
    droppable_tags = ["POS"]

    def __init__(self, id: str = None, text: str = None, tokens: list = None, mention=None, doc_id: UUID = None):
        self.id: str = id
        self.text: str = text
        self.tokens: list = tokens
        self.mention = mention
        self.doc_id: UUID = doc_id
        self.subset: list["Entity"] = []
        self._tree_node: dict = None
        self.encoding: tf.Tensor = None
        self.encoding_count: int = 0

    @staticmethod
    def build_id(doc_id=None, tokens=None, mention=None):
        if mention:
            mentioned_entity = re.sub(r'\s', '-', mention.entityMentionText)
            return f"NE-{mention.entityType}-{mentioned_entity}"
        token_sections = [f"{t.tokenBeginIndex}-{t.value}" for t in tokens]
        return str(doc_id) + "-" + re.sub(r"\s", "", "-".join(token_sections))

    @staticmethod
    def from_mention(mention, all_tokens):
        tokens = all_tokens[mention.tokenStartInSentenceInclusive:mention.tokenEndInSentenceExclusive]
        text = mention.entityMentionText
        return Entity(text=text, tokens=tokens, mention=mention)

    @staticmethod
    def from_tokens(doc_id, tokens, text=None):
        text = text or " ".join([token.value for token in tokens])
        return Entity(text=text, tokens=tokens, doc_id=doc_id)

    def dynamic_id(self):
        return Entity.build_id(mention=self.mention) if self.mention else Entity.build_id(self.doc_id, self.tokens)

    def includes(self, target: "Entity"):
        if self.tokens is None or target.tokens is None or len(self.tokens) <= len(target.tokens):
            return False
        for token in target.tokens:
            if token not in self.tokens:
                return False
        return True

    def add_to_subset(self, entity: "Entity"):
        self.subset.append(entity)

    def remove_from_subset(self, entity: "Entity"):
        self.subset.remove(entity)

    def get_final_entity(self, tree: "TokenTree"):
        if self.subset:
            return self._get_derived_entities(tree)["main"].get_final_entity(tree)
        return self

    def build_derived_triples(self, tree: "TokenTree"):
        derived_entities = self._get_derived_entities(tree)
        if derived_entities is None:
            return []
        main_entity: "Entity" = derived_entities["main"]
        other_entities: list["Entity"] = derived_entities["others"]
        return [(main_entity.get_final_entity(tree), other_entity._get_entity_tree_node(tree)["relation"], other_entity.get_final_entity(tree)) for other_entity in other_entities]

    def trim(self):
        start_index = 0
        end_index = len(self.tokens)
        changed = True
        while changed:
            if start_is_trimmable := self.tokens[start_index].pos in self.trimmable_tags:
                start_index += 1
            if end_is_trimmable := self.tokens[end_index-1].pos in self.trimmable_tags:
                end_index -= 1
            changed = start_is_trimmable or end_is_trimmable
        tokens = self.tokens[start_index:end_index]
        return Entity.from_tokens(self.doc_id, tokens)

    def add_encoding(self, encoding):
        if self.encoding_count == 0:
            self.encoding = encoding
        else:
            self.encoding = (self.encoding * self.encoding_count + encoding) / (self.encoding_count + 1)
        self.encoding_count += 1

    def is_named_entity(self):
        id = self.id if self.id else self.dynamic_id()
        return id.startswith("NE-")

    def compare(self, other: "Entity"):
        return tf.tensordot(tf.math.l2_normalize(self.encoding, 0), tf.math.l2_normalize(other.encoding, 0), 1).numpy()

    def __repr__(self):
        return f'<Entity{" NER" if self.is_named_entity() else ""} "{self.text}">'

    def _get_derived_entities(self, tree: "TokenTree"):
        if self.subset:
            derived_entities = [*self.subset]
            subset_tokens = [token for subset_e in self.subset for token in subset_e.tokens]
            slice_start = slice_end = None
            for i, token in enumerate(self.tokens):
                if token not in subset_tokens:
                    slice_start = slice_start or i
                    slice_end = i + 1
                if (token in subset_tokens or i == len(self.tokens) - 1) and slice_start is not None:
                    tokens = self.tokens[slice_start:slice_end]
                    entity = Entity.from_tokens(self.doc_id, tokens)
                    derived_entities.append(entity)
                    slice_start = slice_end = None
            main_derived_entity = sorted(derived_entities, key=lambda e: (e._get_entity_tree_node(tree)["level"], -1 if e.is_named_entity() else 1))[0]
            derived_entities.remove(main_derived_entity)
            return {"main": main_derived_entity, "others": derived_entities}
        return None

    def _get_entity_tree_node(self, tree: "TokenTree"):
        if not self._tree_node:
            self._tree_node = tree.fetch(tokens=self.tokens)
        return self._tree_node