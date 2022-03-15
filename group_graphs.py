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
    for i_filename, j_filename, similarity in sorted_mappings:
        group_size = group_sizes[0]
        i_group = get_current_group(i_filename, groups)
        j_group = get_current_group(j_filename, groups)

        if group_size > 1:
            if i_group is None and j_group is None:
                group = {i_filename, j_filename}
                groups.append(group)
            elif i_group is None or j_group is None:
                group = i_group or j_group
                if len(group) < group_size:
                    group.add(i_filename)
                    group.add(j_filename)
            elif len(i_group) + len(j_group) <= group_size:
                group = i_group
                group.update(j_group)
                groups.remove(j_group)
            if len(group) >= group_size:
                group_sizes.pop(0)
        else:
            if i_group is None:
                groups.append({i_filename})
                group_sizes.pop(0)
            if j_group is None:
                groups.append({j_filename})
                group_sizes.pop(0)
        
        if len(group_sizes) < 1:
            break

    return groups

def merge_graphs(models, files, ratio=RATIO, threshold=THRESHOLD):
    triples = np.array([(node["subject"], node["relation"], node["object"]) for file in files for node in read_json(file)])
    merged_graph = build_graph(models, triples[:, 0], triples[:, 1], triples[:, 2], ratio=ratio, threshold=threshold)

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