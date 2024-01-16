import json
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tqdm import tqdm

from ..models.graph import Graph
from ..models.encoder import Encoder
from ...constants import GRAPH_DIR
from ...utils.batch_data.helpers import set_batch_data, save_batch_params

from ...languages import Language


def build_bridges(language: Language, batch: str, size, ratio, threshold, batch_size):
    kg_dir = GRAPH_DIR / language / batch
    bridge_dir = kg_dir / "bridges"
    bridge_dir.mkdir(exist_ok=True)

    encoder = Encoder(size=size, language=language, ratio=ratio)

    set_batch_data(language, batch, "bridges", "started")
    try:
        _build_bridges(kg_dir, encoder, threshold, batch_size)
        set_batch_data(language, batch, "bridges", "done")
    except Exception:
        set_batch_data(language, batch, "bridges", "failed")


def _build_bridges(kg_dir: Path, encoder, threshold, batch_size):
    graph_dir = kg_dir / "clean"
    bridge_dir = kg_dir / "bridges"
    bridge_dir.mkdir(exist_ok=True)

    graph_files = [file for file in graph_dir.glob("*.json")]
    for source_file in tqdm(graph_files):
        bridges = _get_existing_bridges(bridge_dir, source_file)
        target_files = [file for file in graph_files if file.name not in bridges and file != source_file]
        if target_files:
            graph = Graph.from_json(source_file, encoder).build_entity_encodings(batch_size)
            for target_file in tqdm(target_files, leave=False):
                target_graph = Graph.from_json(target_file, encoder).build_entity_encodings(batch_size)
                bridges[target_file.name] = graph.build_bridges(target_graph, threshold)
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


def _get_dir(language, name):
    if language and name:
        return GRAPH_DIR / language / name

    base_dir = GRAPH_DIR / language if language else GRAPH_DIR
    window = Tk()
    window.withdraw()
    window.attributes("-topmost", 1)
    directory = askdirectory(initialdir=base_dir)

    return Path(directory)


if __name__ == "__main__":
    from .cli_args import LANGUAGE, NAME, SIZE, RATIO, THRESHOLD, BATCH_SIZE

    kg_dir = _get_dir(LANGUAGE, NAME)
    language: Language = LANGUAGE if LANGUAGE else kg_dir.parent.name  # type: ignore
    name = NAME if NAME else kg_dir.name

    save_batch_params(language, name, "bridges", {
        "size": SIZE,
        "extraction_model": "default",
        "ratio": RATIO,
        "threshold": THRESHOLD,
        "batch_size": BATCH_SIZE,
    })

    build_bridges(language, name, SIZE, RATIO, THRESHOLD, BATCH_SIZE)
