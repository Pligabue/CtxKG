from pathlib import Path
import json

from cli_args import MATCH


def get_id_to_text_map(graph):
    id_to_text_map = {}
    for node in graph:
        id_to_text_map[node["subject_id"]] = node["subject"]
        id_to_text_map[node["object_id"]] = node["object"]
    return id_to_text_map

def is_same_triple(a_node, b_node):
    return (a_node["subject_id"] == b_node["subject_id"] and
            a_node["relation"] == b_node["relation"] and
            a_node["object_id"] == b_node["object_id"])

def node_already_exists(nodes, new_node):
    for node in nodes:
        if is_same_triple(node, new_node):
            return True
    return False

def get_entities_sorted_by_freq(graph):
    entity_counter = {}
    for node in graph:
        entities = [node["subject_id"]] + node["subject_links"] + [node["object_id"]] + node["object_links"]
        for entity in entities:
            if entity in entity_counter:
                entity_counter[entity] += 1
            else:
                entity_counter[entity] = 1
    return sorted(entity_counter.keys(), key=lambda entity: entity_counter[entity], reverse=True)

def get_most_frequent_entity(sorted_entity_ids, pool):
    for entity_id in sorted_entity_ids:
        if entity_id in pool:
            return entity_id

def update_graph(graph, id_to_text_map, old_entity_id, new_entity_id):
    return [{
        "subject_links": [new_entity_id if link == old_entity_id else link for link in node["subject_links"]],
        "subject_id": new_entity_id if node["subject_id"] == old_entity_id else node["subject_id"],
        "subject": id_to_text_map[new_entity_id] if node["subject_id"] == old_entity_id else node["subject"],
        "relation": node["relation"],
        "object": id_to_text_map[new_entity_id] if node["object_id"] == old_entity_id else node["object"],
        "object_id": new_entity_id if node["object_id"] == old_entity_id else node["object_id"],
        "object_links": [new_entity_id if link == old_entity_id else link for link in node["object_links"]]
    } for node in graph]

def remove_links(graph, base_id_to_clean_id_map, id_to_text_map):
    clean_graph = []
    for node in graph:
        clean_subject_id = base_id_to_clean_id_map[node["subject_id"]]
        clean_subject = id_to_text_map[clean_subject_id]
        clean_object_id = base_id_to_clean_id_map[node["object_id"]]
        clean_object = id_to_text_map[clean_object_id]
        clean_graph.append({
            "subject_id": clean_subject_id,
            "subject": clean_subject,
            "relation": node["relation"],
            "object": clean_object,
            "object_id": clean_object_id
        })
    return clean_graph

def remove_duplicates(graph):
    node_sets = {frozenset(node.items()) for node in graph}
    final_graph = []
    for node_set in node_sets:
        node = dict(node_set)
        final_graph.append({
            "subject_id": node["subject_id"],
            "subject": node["subject"],
            "relation": node["relation"],
            "object": node["object"],
            "object_id": node["object_id"]
        })
    return final_graph

def clean_graph(graph):
    id_to_text_map = get_id_to_text_map(graph)
    sorted_entity_ids = get_entities_sorted_by_freq(graph)
    base_id_to_clean_id_map = {}
    for node in graph:
        subject_ids = [node["subject_id"]] + node["subject_links"]
        clean_subject_id = get_most_frequent_entity(sorted_entity_ids, subject_ids)
        for subject_id in subject_ids:
            base_id_to_clean_id_map[subject_id] = clean_subject_id
        object_ids = [node["object_id"]] + node["object_links"]
        clean_object_id = get_most_frequent_entity(sorted_entity_ids, object_ids)
        for object_id in object_ids:
            base_id_to_clean_id_map[object_id] = clean_object_id
    graph = remove_links(graph, base_id_to_clean_id_map, id_to_text_map)
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