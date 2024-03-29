from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askdirectory

from ..models.graph import Graph
from ..models.encoder import Encoder
from ...constants import GRAPH_DIR
from ...utils.batch_data.helpers import set_batch_data

from ...languages import Language


def clean_batch(language: Language, batch: str):
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
    from .cli_args import LANGUAGE, NAME

    if LANGUAGE and NAME:
        batch_dir = GRAPH_DIR / LANGUAGE / NAME
    else:
        base_dir = GRAPH_DIR / LANGUAGE if LANGUAGE else GRAPH_DIR
        Tk().withdraw()
        directory = askdirectory(initialdir=base_dir)
        batch_dir = Path(directory)

    language: Language = LANGUAGE if LANGUAGE else batch_dir.parent.name  # type: ignore
    batch = NAME if NAME else batch_dir.name

    clean_batch(language, batch)
