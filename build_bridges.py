from pathlib import Path
from operator import attrgetter
import json
from tkinter import Tk
from tkinter.filedialog import askdirectory

from tqdm import tqdm

from src.graph import Graph
from src.encoder import Encoder
from constants import RESULT_DIR
from cli_args import MATCH, SIZE, CLEAN, OVERWRITE, RATIO, THRESHOLD


def get_dirs(match):
    if match is None:
        Tk().withdraw()
        directory = askdirectory(initialdir=RESULT_DIR)
        return [Path(directory)]
    return [path for path in RESULT_DIR.glob(match) if path.is_dir()]

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize(bridge_dir):
    reversed_files = sorted(bridge_dir.glob("*.json"), key=attrgetter("name"), reverse=True)
    for file in reversed_files[:-1]:
        bridges = read_json(file)
        for target_file in reversed_files[reversed_files.index(file)+1:]:
            target_bridges = read_json(target_file)
            bridges[target_file.name] = {value: key for key, value in target_bridges[file.name].items()}
        with file.open("w", encoding="utf-8") as f:
            json.dump(bridges, f, indent=2)

def main(match, size, clean, overwrite, ratio, threshold):
    kg_dirs = get_dirs(match)

    encoder = Encoder(size=size, ratio=ratio)

    for dir in kg_dirs:
        graph_dir = dir / "clean" if clean else dir / "base"
        bridge_dir = graph_dir / "bridges"
        bridge_dir.mkdir(exist_ok=True)
        
        graph_files = [file for file in graph_dir.glob("*.json") if overwrite or not (bridge_dir / file.name).exists()]
        graph_files.sort(key=attrgetter("name"))
        for graph_file in tqdm(graph_files):
            bridges = {}
            graph = Graph.from_json(graph_file).add_encoder(encoder).build_entity_encodings()
            target_graph_files = graph_files[graph_files.index(graph_file)+1:]
            for target_graph_file in tqdm(target_graph_files, leave=False):
                target_graph = Graph.from_json(target_graph_file).add_encoder(encoder).build_entity_encodings()
                bridges[target_graph_file.name] = graph.build_bridges(target_graph, threshold)
            with (bridge_dir / graph_file.name).open("w", encoding="utf-8") as f:
                json.dump(bridges, f, indent=2)

        normalize(bridge_dir)

if __name__ == "__main__":
    main(MATCH, SIZE, CLEAN, OVERWRITE, RATIO, THRESHOLD)