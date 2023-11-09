from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askdirectory

from ..models.graph import Graph
from ..models.encoder import Encoder
from ...constants import GRAPH_DIR
from ...utils.batch_data import set_batch_data


def clean_batch(language: str, batch: str):
    batch_dir = GRAPH_DIR / language / batch

    set_batch_data(language, batch, "clean", "started")
    try:
        _clean_dir(batch_dir)
        set_batch_data(language, batch, "clean", "done")
    except Exception:
        set_batch_data(language, batch, "clean", "failed")


def _clean_dir(batch_dir: Path):
    base_dir = batch_dir / "base"
    clean_dir = batch_dir / "clean"
    clean_dir.mkdir(exist_ok=True)
    encoder = Encoder()

    clean_graph_names = [f.stem for f in clean_dir.glob("*.json")]
    graphs_to_be_cleaned = [f for f in base_dir.glob("*.json") if f.stem not in clean_graph_names]
    for file in graphs_to_be_cleaned:
        graph = Graph.from_json(file, encoder)
        graph.clean()
        graph.save_json(clean_dir / file.name)


if __name__ == "__main__":
    Tk().withdraw()
    directory = askdirectory(initialdir=GRAPH_DIR)
    batch_dir = Path(directory)
    _clean_dir(batch_dir)
