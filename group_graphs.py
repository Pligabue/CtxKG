import numpy as np
import pandas as pd
from pathlib import Path
import json
import math

from tqdm import tqdm

from build_kg_nodes import get_models, build_graph
from clean_nodes import clean_graph
from cli_args import GROUPS, MATCH, SIZE, RATIO, THRESHOLD, CLEAN


def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_sorted_mappings(filenames, sim_matrix):
    mappings = []
    for i, i_filename in enumerate(filenames):
        for j, j_filename in enumerate(filenames[i+1:]):
            mappings.append((i_filename, j_filename, sim_matrix[i][i+j+1]))
    return sorted(mappings, key=lambda mapping: mapping[2], reverse=True)

def get_current_group(item, groups):
    for group in groups:
        if item in group:
            return group
    return None

def get_next_member(group, mappings):
    for i_filename, j_filename, similarity in mappings:
        if i_filename in group and j_filename not in group:
            return j_filename
        if i_filename not in group and j_filename in group:
            return i_filename

def get_group_sizes(n_of_items):
    group_sizes = []
    remaining_items = n_of_items
    remaining_groups = GROUPS
    while remaining_items > 0:
        current_size = math.ceil(remaining_items / remaining_groups)
        group_sizes.append(current_size)
        remaining_items -= current_size
        remaining_groups -= 1
    return group_sizes

def get_groups(filenames, sim_matrix):
    sorted_mappings = get_sorted_mappings(filenames, sim_matrix)
    group_sizes = get_group_sizes(len(filenames))

    groups = []
    while sorted_mappings:
        i_filename, j_filename, similarity = sorted_mappings.pop(0)
        group_size = group_sizes.pop(0)

        if group_size > 1:
            group = {i_filename, j_filename}
            while sorted_mappings:
                if len(group) >= group_size:
                        break
                next_member = get_next_member(group, sorted_mappings)
                group.add(next_member)
            groups.append(group)
            if len(group_sizes) < 1:
                    break
            sorted_mappings = [mapping for mapping in sorted_mappings if mapping[0] not in group and mapping[1] not in group]
        else:
            individual_group_filenames = {filename for mapping in sorted_mappings for filename in mapping[:2]}
            for filename in individual_group_filenames:
                groups.append({filename})
            break

    return groups

def merge_graphs(models, files, ratio=RATIO, threshold=THRESHOLD):
    triples = np.array([(node["subject"], node["relation"], node["object"], node["subject_id"], node["object_id"]) for file in files for node in read_json(file)])
    merged_graph = build_graph(models, triples[:, 0], triples[:, 1], triples[:, 2], triples[:, 3], triples[:, 4], ratio=ratio, threshold=threshold)

    return merged_graph

def main():
    RESULT_DIR = Path('./results')
    KG_NODE_DIRS = [dir for dir in RESULT_DIR.glob(MATCH) if (dir / "clean").is_dir() and (dir / "doc_similarity.json").is_file()]

    models = get_models(size=SIZE)

    for dir in KG_NODE_DIRS:
        clean_dir = dir / "clean"

        doc_similarities = read_json(dir / "doc_similarity.json")
        filenames = doc_similarities["filenames"]
        sim_matrix = doc_similarities["similarity_matrix"]

        groups = get_groups(filenames, sim_matrix)

        groups_dir = dir / "merged"
        groups_dir.mkdir(exist_ok=True)
        groups_dir = groups_dir / f"groups_{GROUPS}_ratio_{int(RATIO * 100)}_threshold_{int(THRESHOLD * 100)}_{SIZE}{'_clean' if CLEAN else ''}"
        groups_dir.mkdir(exist_ok=True)

        enumerated_groups = list(enumerate(groups))
        for i, group in tqdm(enumerated_groups):
            files = [file for file in clean_dir.glob("*.json") if file.stem in group]
            merged_graph = merge_graphs(models, files)
            if CLEAN:
                merged_graph = clean_graph(merged_graph)

            data = {
                "filenames": list(group),
                "nodes": merged_graph
            }

            with open(groups_dir / f"group_{i}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()