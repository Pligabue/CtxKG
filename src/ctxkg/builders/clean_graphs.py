from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askdirectory

from .cli_args import MATCH
from ..models.graph import Graph
from ..models.encoder import Encoder
from ...constants import GRAPH_DIR


def get_dirs(match):
    if match is None:
        Tk().withdraw()
        directory = askdirectory(initialdir=GRAPH_DIR)
        return [Path(directory)]
    return [path for path in GRAPH_DIR.glob(match) if path.is_dir()]


def main(match):
    dirs = get_dirs(match)

    for dir in dirs:
        base_dir = dir / "base"
        clean_dir = dir / "clean"
        clean_dir.mkdir(exist_ok=True)
        encoder = Encoder()

        for file in base_dir.glob("*.json"):
            graph = Graph.from_json(file, encoder)
            graph.clean()
            graph.save_json(clean_dir / file.name)


if __name__ == "__main__":
    main(MATCH)
