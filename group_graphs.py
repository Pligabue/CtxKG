import re
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
import json
from datetime import datetime

from tqdm import tqdm

from build_kg_nodes import get_models, build_graph
from cli_args import GROUP_SIZE, MATCH, SIZE, RATIO, THRESHOLD


def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_sorted_mappings(filenames, sim_matrix):
    mappings = []
    for i in range(len(filenames)):
        for j in range(i + 1, len(filenames)):
            mappings.append((i, j, sim_matrix[i][j]))

    return sorted(mappings, key=lambda mapping: mapping[2], reverse=True)

def get_current_group(item, groups):
    for group in groups:
        if item in group:
            return group
    return None

def get_groups(sorted_mappings, filenames):
    groups = []
    for i, j, similarity in sorted_mappings:
        i_group = get_current_group(i, groups)
        j_group = get_current_group(j, groups)

        if i_group is None and j_group is None:
            groups.append({i, j})
        elif i_group is None or j_group is None:
            group = i_group or j_group
            if len(group) < GROUP_SIZE:
                group.add(i)
                group.add(j)

    return [[filenames[index] for index in group] for group in groups]

def merge_graphs(group, clean_dir):
    files = [file for file in clean_dir.glob("*.json") if file.stem in group]
    node_groups = [read_json(file) for file in files]
    
    final_nodes = []
    for node_group in node_groups:
        final_nodes += node_groups

    return final_nodes

def main():
    RESULT_DIR = Path('./results')
    KG_NODE_DIRS = [dir for dir in RESULT_DIR.glob(MATCH) if (dir / "clean").is_dir() and (dir / "doc_similarity.json").is_file()]

    for dir in KG_NODE_DIRS:
        clean_dir = dir / "clean"

        doc_similarities = read_json(dir / "doc_similarity.json")
        filenames = doc_similarities["filenames"]
        sim_matrix = doc_similarities["similarity_matrix"]

        sorted_mappings = get_sorted_mappings(filenames, sim_matrix)
        groups = get_groups(sorted_mappings, filenames)

        merged_dir = dir / "merged"
        merged_dir.mkdir(exist_ok=True)
        groups_dir = merged_dir / f"group_size_{GROUP_SIZE}"
        groups_dir.mkdir(exist_ok=True)

        for i, group in enumerate(groups):
            merged_graph = merge_graphs(group, clean_dir)
            data = {
                "filenames": group,
                "nodes": merged_graph
            }

            with open(groups_dir / f"group_{i}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()