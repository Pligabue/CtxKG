from pathlib import Path
import json

from cli_args import MATCH

def is_same_triple(a_node, b_node):
    return (a_node["subject"] == b_node["subject"] and
            a_node["relation"] == b_node["relation"] and
            a_node["object"] == b_node["object"])

def node_already_exists(nodes, new_node):
    for node in nodes:
        if is_same_triple(node, new_node):
            return True
    return False

def get_entities_sorted_by_freq(graph):
    entity_counter = {}
    for node in graph:
        entities = [node["subject"]] + node["subject_links"] + [node["object"]] + node["object_links"]
        for entity in entities:
            if entity in entity_counter:
                entity_counter[entity] += 1
            else:
                entity_counter[entity] = 1
    return sorted(entity_counter.keys(), key=lambda entity: entity_counter[entity], reverse=True)

def get_most_frequent_entity(sorted_entities, pool):
    for entity in sorted_entities:
        if entity in pool:
            return entity

def update_graph(graph, old_entity, new_entity):
    return [{
        "subject": new_entity if node["subject"] == old_entity else node["subject"],
        "subject_links": [new_entity if link == old_entity else link for link in node["subject_links"]],
        "relation": node["relation"],
        "object": new_entity if node["object"] == old_entity else node["object"],
        "object_links": [new_entity if link == old_entity else link for link in node["object_links"]]
    } for node in graph]

def remove_links(graph):
    return [{"subject": node["subject"], "relation": node["relation"], "object": node["object"]} for node in graph]

def remove_duplicates(graph):
    node_set = {frozenset(node.items()) for node in graph}
    return [dict(node) for node in node_set]

def clean_graph(graph):
    sorted_entities = get_entities_sorted_by_freq(graph)
    for node in graph:
        subjects = [node["subject"]] + node["subject_links"]
        clean_subject = get_most_frequent_entity(sorted_entities, subjects)
        graph = update_graph(graph, node["subject"], clean_subject)
        objects = [node["object"]] + node["object_links"]
        clean_object = get_most_frequent_entity(sorted_entities, objects)
        graph = update_graph(graph, node["object"], clean_object)
    graph = remove_links(graph)
    graph = remove_duplicates(graph)
    return graph

def main():
    RESULTS_PATH = Path("./results")
    dirs = [dir for dir in RESULTS_PATH.glob(MATCH) if dir.is_dir()]

    for dir in dirs:
        BASE_DIR = dir / "base"
        CLEAN_DIR = dir / "clean"
        CLEAN_DIR.mkdir(exist_ok=True)
        
        for file in BASE_DIR.glob("*.json"):
            with open(file) as f:
                graph = json.load(f)

            cleaned_graph = clean_graph(graph)

            with open(CLEAN_DIR / file.name, "w", encoding="utf-8") as f:
                json.dump(cleaned_graph, f, indent=2)

if __name__ == "__main__":
    main()