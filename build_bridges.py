from pathlib import Path
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
        window = Tk()
        window.withdraw()
        window.attributes("-topmost", 1)
        directory = askdirectory(initialdir=RESULT_DIR)
        return [Path(directory)]
    return [path for path in RESULT_DIR.glob(match) if path.is_dir()]

def save_params(dir, size, ratio, threshold, match):
    with (dir / "PARAMS.md").open("w", encoding="utf-8") as f:
        params = (f"BERT SIZE: {size}\n" \
                  f"RATIO (entity encoding over full sentence encoding): {ratio}\n" \
                  f"THRESHOLD: {threshold}\n" \
                  f"FILE NAME MATCHING: {match}\n")
        f.write(params)

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_existing_bridges(bridge_dir: Path, source_file: Path):
    bridge_file = bridge_dir / source_file.name
    bridges = {} if not bridge_file.is_file() else read_json(bridge_file)
    missing_files = [f for f in bridge_dir.glob("*.json") if f.name not in bridges]
    for target_file in missing_files:
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
        save_params(bridge_dir, size, ratio, threshold, match)
        
        graph_files = [file for file in graph_dir.glob("*.json")]
        for source_file in tqdm(graph_files):
            bridges = get_existing_bridges(bridge_dir, source_file)
            target_files = [file for file in graph_files if file.name not in bridges and file != source_file]
            if target_files:
                graph = Graph.from_json(source_file, encoder).build_entity_encodings()
                for target_files in tqdm(target_files, leave=False):
                    target_graph = Graph.from_json(target_files, encoder).build_entity_encodings()
                    bridges[target_files.name] = graph.build_bridges(target_graph, threshold)
            with (bridge_dir / source_file.name).open("w", encoding="utf-8") as f:
                json.dump(bridges, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main(MATCH, SIZE, CLEAN, RATIO, THRESHOLD)