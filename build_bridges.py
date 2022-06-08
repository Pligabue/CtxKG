from pathlib import Path
from operator import attrgetter
import json
from tkinter import Tk
from tkinter.filedialog import askdirectory

from tqdm import tqdm

from src.graph import Graph
from src.encoder import Encoder
from constants import RESULT_DIR
from cli_args import MATCH, SIZE, CLEAN, RATIO, THRESHOLD


def get_dirs(match):
    if match is None:
        Tk().withdraw()
        directory = askdirectory(initialdir=RESULT_DIR)
        return [Path(directory)]
    return [path for path in RESULT_DIR.glob(match) if path.is_dir()]

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_existing_bridges(bridge_dir, source_file):
    bridges = {}
    for target_file in bridge_dir.glob("*.json"):
        target_bridges = read_json(target_file)
        if source_file.name in target_bridges:
            bridges[target_file.name] = {value: key for key, value in target_bridges[source_file.name].items()}
    return bridges

def main(match, size, clean, ratio, threshold):
    kg_dirs = get_dirs(match)
    encoder = Encoder(size=size, ratio=ratio)

    for dir in kg_dirs:
        graph_dir = dir / "clean" if clean else dir / "base"
        bridge_dir = graph_dir / "bridges"
        bridge_dir.mkdir(exist_ok=True)
        
        graph_files = [file for file in graph_dir.glob("*.json")]
        for source_file in tqdm(graph_files):
            bridges = get_existing_bridges(bridge_dir, source_file)
            graph = Graph.from_json(source_file).add_encoder(encoder).build_entity_encodings()
            target_files = [file for file in graph_files if file.name not in bridges and file != source_file]
            for target_files in tqdm(target_files, leave=False):
                target_graph = Graph.from_json(target_files).add_encoder(encoder).build_entity_encodings()
                bridges[target_files.name] = graph.build_bridges(target_graph, threshold)
            with (bridge_dir / source_file.name).open("w", encoding="utf-8") as f:
                json.dump(bridges, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main(MATCH, SIZE, CLEAN, RATIO, THRESHOLD)