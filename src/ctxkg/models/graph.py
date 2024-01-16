from typing import Dict, Union
import numpy as np
import pandas as pd
import tensorflow as tf
import json
from pathlib import Path
import re

from .encoder import Encoder
from .entity import Entity
from .triple import Triple
from .link import Link


class Graph:
    def __init__(self, filepath: str, encoder: Encoder, normalize=True):
        self.filepath = filepath
        self.encoder = encoder
        self.normalize = normalize
        self.entities: Dict[str, Entity] = {}
        self.triples: list[Triple] = []
        self.links: list[Link] = []

    @staticmethod
    def from_csv(filepath: Union[str, Path], encoder: Encoder):
        graph = Graph("", encoder)
        with open(filepath, encoding="utf-8") as f:
            if m := re.match(r"# (?P<filepath>.*)", f.readline()):
                graph.filepath = m["filepath"]
            df = pd.read_csv(f, sep=";", comment="#")

        for i, row in df.iterrows():
            confidence: float = row["confidence"]  # type: ignore
            subject_text: str = row["subject"]     # type: ignore
            relation: str = row["relation"]        # type: ignore
            object_text: str = row["object"]       # type: ignore
            subject_id: str = row["subject_id"]    # type: ignore
            object_id: str = row["object_id"]      # type: ignore

            subject = graph.get_entity_by_id(subject_id, subject_text)
            object = graph.get_entity_by_id(object_id, object_text)
            graph.add_triple(subject, relation, object, confidence=confidence)

        return graph

    @staticmethod
    def from_json(filepath: Union[str, Path], encoder: Encoder):
        graph = Graph("", encoder)
        with open(filepath, encoding="utf-8") as f:
            graph_json = json.load(f)
            graph.filepath = graph_json["document"]
            for id, text in graph_json["entities"].items():
                graph.add_entity(id, text)
            for node in graph_json["graph"]:
                subject = graph.get_entity_by_id(node["subject_id"])
                relation = node["relation"]
                object = graph.get_entity_by_id(node["object_id"])
                graph.add_triple(subject, relation, object)
            for id, links in graph_json["links"].items():
                entity = graph.get_entity_by_id(id)
                for link in links:
                    linked_entity = graph.get_entity_by_id(link)
                    if not graph.link_exists(entity, linked_entity):
                        graph.add_link(entity, linked_entity)
        return graph

    def get_entity_by_id(self, entity_id: str, entity_text=""):
        if entity_id in self.entities:
            return self.entities[entity_id]
        return self.add_entity(entity_id, entity_text)

    def add_encoder(self, encoder: Encoder):
        self.encoder = encoder
        return self

    def add_entity(self, id: str, text: str):
        new_entity = Entity(id, text)
        self.entities[id] = new_entity
        return new_entity

    def add_triple(self, subject: Entity, relation_text: str, object: Entity, confidence=1.0):
        new_triple = Triple(subject, relation_text, object, confidence=confidence)
        self.triples.append(new_triple)
        return new_triple

    def add_link(self, entity_a: Entity, entity_b: Entity):
        new_link = Link(entity_a, entity_b)
        self.links.append(new_link)
        return new_link

    def get_linked_entities(self, entity: Entity):
        linked_entities: list[Entity] = []
        for link in self.links:
            if link.entity_a is not entity and link.entity_b is not entity:
                continue
            linked_entity = link.entity_a if link.entity_b is entity else link.entity_b
            linked_entities.append(linked_entity)  # type: ignore
        return linked_entities

    def link_exists(self, entity_a: Entity, entity_b: Entity):
        return entity_b in self.get_linked_entities(entity_a)

    def build_entity_encodings(self, batch_size=None):
        self.encoder.build_entity_encodings(self.triples, batch_size)
        return self

    def get_stacked_encodings(self):
        encodings = [entity.encoding for entity in self.entities.values()]
        return tf.math.l2_normalize(encodings, 1) if self.normalize else encodings

    def build_links(self, threshold: float):
        self.links = []
        entities = list(self.entities.values())
        for i, entity in enumerate(entities[:-1]):
            pool = entities[i+1:]
            entity_encoding = tf.math.l2_normalize([entity.encoding], 1) if self.normalize else [entity.encoding]
            pool_encodings = [e.encoding for e in pool]
            pool_encodings = tf.math.l2_normalize(pool_encodings, 1) if self.normalize else pool_encodings
            similarity = tf.linalg.matmul(entity_encoding, pool_encodings, transpose_b=True).numpy()
            similarity_mask = similarity[0] >= threshold
            for candidate_link, should_link in zip(pool, similarity_mask):
                if should_link:
                    self.add_link(entity, candidate_link)
        return self

    def build_triple_json(self, triple: Triple):
        return {"subject_id": triple.subject.id, "relation": triple.relation, "object_id": triple.object.id}

    def save_json(self, filepath: Union[str, Path]):
        graph_json = {
            "document": Path(self.filepath).resolve().as_posix(),
            "entities": {entity_id: entity.text for entity_id, entity in self.entities.items()},
            "graph": [self.build_triple_json(t) for t in self.triples],
            "links": {
                e_id: [linked_e.id for linked_e in self.get_linked_entities(e)] for e_id, e in self.entities.items()
            },
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(graph_json, f, indent=2, ensure_ascii=False)
        return self

    def number_of_appearences(self, entity):
        return len([triple for triple in self.triples if triple.includes_entity(entity)])

    def get_replacement(self, pool: list[Entity], sorted_by_appearences: list[Entity]):
        for entity in sorted_by_appearences:
            if entity in pool:
                return entity
        return None

    def replace_entity_in_triples(self, original: Entity, replacement: Entity):
        for triple in self.triples:
            triple.replace_entity(original, replacement)

    def get_first_appearance(self, target_triple: Triple):
        for triple in self.triples:
            if triple == target_triple:
                return triple
        return None

    def get_entity_priority(self, entity: Entity):
        return (entity.is_named_entity(), self.number_of_appearences(entity))

    def clean(self):
        entity_list = list(self.entities.values())
        sorted_entities = sorted(entity_list, key=self.get_entity_priority, reverse=True)
        for entity in entity_list:
            entity_pool = [entity] + self.get_linked_entities(entity)
            replacement = self.get_replacement(entity_pool, sorted_entities)
            if replacement and entity is not replacement:
                self.replace_entity_in_triples(entity, replacement)
                self.links = [l for l in self.links if l.entity_a is not entity and l.entity_b is not entity]
                del self.entities[entity.id]
        self.remove_duplicates()
        self.remove_tripleless_entities()
        self.links = []
        return self

    def remove_duplicates(self):
        self.triples = [triple for triple in self.triples if triple is self.get_first_appearance(triple)]
        self.triples = [triple for triple in self.triples if triple.subject is not triple.object]

    def remove_tripleless_entities(self):
        remaining_entities = {entity for triple in self.triples for entity in triple.entities()}
        self.entities = {id: e for id, e in self.entities.items() if e in remaining_entities}

    def build_bridges(self, target_graph: "Graph", threshold: float):
        bridges = {}
        entities = list(self.entities.values())
        target_entities = list(target_graph.entities.values())

        if not (entities and target_entities):
            return bridges

        encodings = self.get_stacked_encodings()
        target_encodings = target_graph.get_stacked_encodings()
        similarity = tf.linalg.matmul(encodings, target_encodings, transpose_b=True).numpy()

        row_matches = {(row, column) for column, row in enumerate(np.argmax(similarity, axis=0))}
        column_matches = {(row, column) for row, column in enumerate(np.argmax(similarity, axis=1))}
        matches = {match for match in column_matches & row_matches if similarity[match[0], match[1]] > threshold}

        for row, column in matches:
            e = entities[row]
            te = target_entities[column]
            bridges[e.id] = te.id

        matching_ids = set(self.entities.keys()) & set(target_graph.entities.keys())
        for matching_id in matching_ids:
            bridges[matching_id] = matching_id

        return bridges
