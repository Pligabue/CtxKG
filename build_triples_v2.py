import uuid
import stanza
from stanza.server import CoreNLPClient

from src.token_tree import TokenTree
from src.triple import Triple
from src.entity import Entity
from constants import STANZA_CORENLP


def build_text_entities(sentence, doc_id):
    entities = {}
    for triple in sentence.openieTriple:
        subject = Entity.from_tokens(doc_id, [sentence.token[t.tokenIndex] for t in triple.subjectTokens], triple.subject)
        object = Entity.from_tokens(doc_id, [sentence.token[t.tokenIndex] for t in triple.objectTokens], triple.object)
        entities[subject.dynamic_id()] = subject
        entities[object.dynamic_id()] = object
    return entities

def build_mention_entities(sentence, doc_id):
    mention_entities = [Entity.from_mention(m, sentence.token) for m in sentence.mentions]
    return {Entity.build_id(doc_id, e.tokens): e for e in mention_entities}

def build_subsets(entities: dict[str, Entity]):
    sorted_entities = sorted(entities.values(), key=lambda e: len(e.tokens), reverse=True)
    for i, source_entity in enumerate(sorted_entities[:-1]):
        for target_entity in sorted_entities[i:]:
            if source_entity.includes(target_entity):
                source_entity.add_to_subset(target_entity)
    for entity in sorted_entities:
        entities_to_remove = [second_dg_e for e in entity.subset for second_dg_e in e.subset if second_dg_e in entity.subset]
        for e in entities_to_remove:
            entity.remove_from_subset(e)
    return entities

def build_entities(sentence, doc_id):
    return build_subsets({**build_text_entities(sentence, doc_id), **build_mention_entities(sentence, doc_id)})

def build_derived_triples(entities: dict[str, Entity], tree):
    return {id: [Triple.build_derived_triple(s, r, o) for s, r, o in e.build_derived_triples(tree)] for id, e in entities.items()}

def main():
    if not STANZA_CORENLP.is_dir():
        stanza.install_corenlp(dir=STANZA_CORENLP.as_posix())

    config = {
        "annotators": ["tokenize", "ssplit", "pos", "lemma", "ner", "depparse", "coref", "natlog" ,"openie"],
        "properties": {
            "openie.max_entailments_per_clause": "100",
            "openie.resolve_coref": "true",
            "openie.ignore_affinity": "true",
            "openie.affinity_probability_cap": "1.0"
        },
        "preload": True,
        "classpath": (STANZA_CORENLP / "*").as_posix(),
        "threads": 2,
        "memory": "2G",
        "start_server": stanza.server.StartServer.TRY_START
    }
    
    with CoreNLPClient(**config) as client:
        triples: list[Triple] = []
        doc_id = uuid.uuid4()
        ann = client.annotate("The great Barack Obama was born in Hawaii.")
        sentences = ann.sentence
        for sen in sentences:
            tree = TokenTree(sen)
            entities = build_entities(sen, doc_id)
            derived_triples = build_derived_triples(entities, tree)
            for triple in sen.openieTriple:
                subject_id = Entity.build_id(doc_id, [sen.token[t.tokenIndex] for t in triple.subjectTokens])
                object_id = Entity.build_id(doc_id, [sen.token[t.tokenIndex] for t in triple.objectTokens])
                t = Triple(entities[subject_id].get_final_entity(tree), triple.relation, entities[object_id].get_final_entity(tree), triple.confidence)
                triples.append(t)
                if subject_id in derived_triples:
                    triples.extend(derived_triples[subject_id])
                    del derived_triples[subject_id]
                if object_id in derived_triples:
                    triples.extend(derived_triples[object_id])
                    del derived_triples[object_id]
        csv = Triple.header("test") + "\n".join(dict.fromkeys([t.as_csv_row() for t in triples]))
        print(csv)

if __name__ == "__main__":
    main()