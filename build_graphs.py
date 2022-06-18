from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

from src.graph import Graph
from src.encoder import Encoder

from constants import TRIPLE_DIR, RESULT_DIR
from cli_args import SIZE, RATIO, THRESHOLD, OVERWRITE, MATCH, NAME


def get_files(base_dir, match, overwrite):
    if match is None:
        Tk().withdraw()
        filenames = askopenfilenames(initialdir=TRIPLE_DIR)
        filepaths = [Path(f) for f in filenames]
    else:
        filepaths = list(TRIPLE_DIR.glob(match))
    return [f for f in filepaths if f.suffix == ".csv" and (overwrite or not (base_dir / f"{f.stem}.json").is_file())]

def main(size, ratio, threshold, overwrite, match, name):
    kg_dir = RESULT_DIR / (name or f"kg_nodes_ratio_{int(100 * ratio)}_threshold_{int(100 * threshold)}_{size}")
    kg_dir.mkdir(exist_ok=True)
    base_dir = kg_dir / "base"
    base_dir.mkdir(exist_ok=True)
    errors_dir = base_dir / "errors"
    errors_dir.mkdir(exist_ok=True)

    failed_files = []
    files = get_files(base_dir, match, overwrite)
    sorted_files = sorted(files, key=lambda file: file.stat().st_size)

    encoder = Encoder(size=size, ratio=ratio)

    for file in tqdm(sorted_files):
        try:
            graph = Graph.from_csv(file, encoder)
            graph.build_entity_encodings()
            graph.build_links(threshold=threshold)
            graph.save_json(base_dir / f"{file.stem}.json")
        except KeyboardInterrupt:
            break
        except Exception as e:
            failed_files.append(f"{datetime.now()}: {file.name} - {e.__class__.__name__}: {e}")

    with open(errors_dir / "failed_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(failed_files))

    return kg_dir

if __name__ == "__main__":
    main(SIZE, RATIO, THRESHOLD, OVERWRITE, MATCH, NAME)