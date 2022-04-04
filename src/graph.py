from typing import Dict, Union
import pandas as pd
import tensorflow as tf
import json

from src.encoder import Encoder
from src.entity import Entity
from src.triple import Triple
from src.link import Link


class Graph:
    def __init__(self, filepaths=None, encoder=None):
        self.filepaths: Union[list[str], None] = filepaths
        self.encoder: Encoder = encoder
        self.entities: Dict[str, Entity] = {}
        self.triples: list[Triple] = []
        self.links: list[Link] = []

    @staticmethod
    def from_csv(filepath):
        graph = Graph([filepath])
        df = pd.read_csv(filepath, sep=";")
        for i, row in df.iterrows():
            confidence = row["confidence"]
            subject_text = row["subject"]
            relation = row["relation"]
            object_text = row["object"]
            subject_id = row["subject_id"]
            object_id = row["object_id"]

            subject = graph.get_entity_by_id(subject_id, subject_text)
            object = graph.get_entity_by_id(object_id, object_text)
            graph.add_triple(subject, relation, object, confidence=confidence) 
        return graph

    @staticmethod
    def from_json(filepath):
        graph = Graph([filepath])
        with open(filepath) as f:
            graph_json = json.load(f)
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

    def get_entity_by_id(self, entity_id, entity_text=""):
        if entity_id in self.entities:
            return self.entities[entity_id]
        return self.add_entity(entity_id, entity_text)
    
    def add_encoder(self, encoder):
        self.encoder = encoder
        return self

    def add_entity(self, id, text):
        new_entity = Entity(id, text)
        self.entities[id] = new_entity
        return new_entity

    def add_triple(self, subject, relation_text, object, confidence=1.0):
        new_triple = Triple(subject, relation_text, object, confidence=confidence)
        self.triples.append(new_triple)
        return new_triple

    def add_link(self, entity_a, entity_b):
        new_link = Link(entity_a, entity_b)
        self.links.append(new_link)
        return new_link

    def get_linked_entities(self, entity):
        return [l.entity_a if l.entity_b is entity else l.entity_b for l in self.links if l.entity_a is entity or l.entity_b is entity]

    def link_exists(self, entity_a, entity_b):
        return entity_b in self.get_linked_entities(entity_a)

    def build_entity_encodings(self):
        subject_encodings, object_encodings = self.encoder.get_entity_encodings(self.triples)
        for triple, subject_encoding, object_encoding in zip(self.triples, subject_encodings, object_encodings):
            triple.subject.add_encoding(subject_encoding)
            triple.object.add_encoding(object_encoding)
        return self

    def build_links(self, threshold):
        self.links = []
        entities = list(self.entities.values())
        for i, entity_a in enumerate(entities):
            for entity_b in entities[i+1:]:
                normalized_a = tf.nn.l2_normalize(entity_a.encoding, 0)        
                normalized_b = tf.nn.l2_normalize(entity_b.encoding, 0)
                cosine = tf.reduce_sum(tf.multiply(normalized_a, normalized_b)).numpy()
                if cosine >= threshold:
                    self.add_link(entity_a, entity_b)
        return self

    def save_json(self, filepath):
        graph_json = {
            "documents": self.filepaths,
            "entities": {entity_id: entity.text for entity_id, entity in self.entities.items()},
            "graph": [{"subject_id": triple.subject.id, "relation": triple.relation, "object_id": triple.object.id} for triple in self.triples],
            "links": {entity_id: [linked_entity.id for linked_entity in self.get_linked_entities(entity)] for entity_id, entity in self.entities.items()}
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(graph_json, f, indent=2)

    def number_of_appearences(self, entity):
        return len([triple for triple in self.triples if triple.includes_entity(entity)])

    def get_replacement(self, pool, sorted_by_appearences):
        for entity in sorted_by_appearences:
            if entity in pool:
                return entity
        return None

    def replace_entity(self, original, replacement):
        del self.entities[original.id]
        for triple in self.triples:
            triple.replace_entity(original, replacement)

    def clean(self):
        sorted_entities = sorted(self.entities.values(), key=lambda entity: self.number_of_appearences(entity), reverse=True)
        for triple in self.triples:
            subject_pool = [triple.subject] + self.get_linked_entities(triple.subject)
            subject_replacement = self.get_replacement(subject_pool, sorted_entities)
            if subject_replacement is not triple.subject and subject_replacement is not None:
                self.replace_entity(triple.subject, subject_replacement)
                sorted_entities.remove(triple.subject)

            object_pool = [triple.object] + self.get_linked_entities(triple.object)
            object_replacement = self.get_replacement(object_pool, sorted_entities)
            if object_replacement is not triple.object and object_replacement is not None:
                self.replace_entity(triple.object, object_replacement)
                sorted_entities.remove(triple.object)
        self.links = []

        return self
