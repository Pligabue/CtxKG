from pathlib import Path
import json
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tqdm import tqdm

from .cli_args import MATCH, SIZE, RATIO, THRESHOLD
from ..models.graph import Graph
from ..models.encoder import Encoder
from ...constants import GRAPH_DIR
from ...utils.batch_data import set_batch_data

from ...languages import Language


def build_bridges(language: Language, batch: str, size, ratio, threshold):
    kg_dir = GRAPH_DIR / language / batch
    bridge_dir = kg_dir / "bridges"
    bridge_dir.mkdir(exist_ok=True)

    _save_params(bridge_dir, size, ratio, threshold)

    encoder = Encoder(size=size, ratio=ratio)

    set_batch_data(language, batch, "bridges", "started")
    try:
        _build_bridge(kg_dir, encoder, threshold)
        set_batch_data(language, batch, "bridges", "done")
    except Exception:
        set_batch_data(language, batch, "bridges", "failed")


def _save_params(dir, size, ratio, threshold):
    with (dir / "PARAMS.md").open("w", encoding="utf-8") as f:
        params = (f"BERT SIZE: {size}\n"
                  f"RATIO (entity encoding over full sentence encoding): {ratio}\n"
                  f"THRESHOLD: {threshold}\n")
        f.write(params)


def _build_bridge(kg_dir: Path, encoder, threshold):
    graph_dir = kg_dir / "clean"
    bridge_dir = kg_dir / "bridges"
    bridge_dir.mkdir(exist_ok=True)

    graph_files = [file for file in graph_dir.glob("*.json")]
    for source_file in tqdm(graph_files):
        bridges = _get_existing_bridges(bridge_dir, source_file)
        target_files = [file for file in graph_files if file.name not in bridges and file != source_file]
        if target_files:
            graph = Graph.from_json(source_file, encoder).build_entity_encodings()
            for target_files in tqdm(target_files, leave=False):
                target_graph = Graph.from_json(target_files, encoder).build_entity_encodings()
                bridges[target_files.name] = graph.build_bridges(target_graph, threshold)
        with (bridge_dir / source_file.name).open("w", encoding="utf-8") as f:
            json.dump(bridges, f, indent=2, ensure_ascii=False)


def _get_existing_bridges(bridge_dir: Path, source_file: Path):
    bridge_file = bridge_dir / source_file.name
    bridges = {} if not bridge_file.is_file() else _read_json(bridge_file)
    missing_files = [f for f in bridge_dir.glob("*.json") if f.name not in bridges]
    for target_file in missing_files:
        target_bridges = _read_json(target_file)
        if source_file.name in target_bridges:
            bridges[target_file.name] = {value: key for key, value in target_bridges[source_file.name].items()}
    return bridges


def _read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_bridges(match, size, ratio, threshold):
    kg_dirs = _get_dirs(match)
    encoder = Encoder(size=size, ratio=ratio)

    for dir in kg_dirs:
        graph_dir = dir / "clean"
        bridge_dir = dir / "bridges"
        bridge_dir.mkdir(exist_ok=True)
        _save_params(bridge_dir, size, ratio, threshold)

        graph_files = [file for file in graph_dir.glob("*.json")]
        for source_file in tqdm(graph_files):
            bridges = _get_existing_bridges(bridge_dir, source_file)
            target_files = [file for file in graph_files if file.name not in bridges and file != source_file]
            if target_files:
                graph = Graph.from_json(source_file, encoder).build_entity_encodings()
                for target_files in tqdm(target_files, leave=False):
                    target_graph = Graph.from_json(target_files, encoder).build_entity_encodings()
                    bridges[target_files.name] = graph.build_bridges(target_graph, threshold)
            with (bridge_dir / source_file.name).open("w", encoding="utf-8") as f:
                json.dump(bridges, f, indent=2, ensure_ascii=False)


def _get_dirs(match):
    if match is None:
        window = Tk()
        window.withdraw()
        window.attributes("-topmost", 1)
        directory = askdirectory(initialdir=GRAPH_DIR)
        return [Path(directory)]
    return [path for path in GRAPH_DIR.glob(match) if path.is_dir()]


if __name__ == "__main__":
    _build_bridges(MATCH, SIZE, RATIO, THRESHOLD)
