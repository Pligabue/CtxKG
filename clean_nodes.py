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

def main():
    RESULTS_PATH = Path("./results")
    dirs = [dir for dir in RESULTS_PATH.glob(MATCH) if dir.is_dir()]

    for dir in dirs:
        BASE_DIR = dir / "base"
        CLEAN_DIR = dir / "clean"
        CLEAN_DIR.mkdir(exist_ok=True)
        
        for file in BASE_DIR.glob("*.json"):
            with open(file) as f:
                nodes = json.load(f)

            entity_counter = {}
            for node in nodes:
                entities = [node["subject"]] + node["subject_links"] + [node["object"]] + node["object_links"]
                for entity in entities:
                    if entity in entity_counter:
                        entity_counter[entity] += 1
                    else:
                        entity_counter[entity] = 1
            
            sorted_entities = sorted(entity_counter.keys(), key=lambda entity: entity_counter[entity], reverse=True)

            clean_nodes = []
            for node in nodes:
                subjects = [node["subject"]] + node["subject_links"]
                for entity in sorted_entities:
                    if entity in subjects:
                        clean_subject = entity
                        break

                objects = [node["object"]] + node["object_links"]
                for entity in sorted_entities:
                    if entity in objects:
                        clean_object = entity
                        break

                clean_node = {
                    "subject": clean_subject,
                    "relation": node["relation"],
                    "object": clean_object
                }

                if not node_already_exists(clean_nodes, clean_node) and clean_subject != clean_object:
                    clean_nodes.append(clean_node)

            with open(CLEAN_DIR / file.name, "w", encoding="utf-8") as f:
                json.dump(clean_nodes, f, indent=2)

if __name__ == "__main__":
    main()