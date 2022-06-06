from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from src.graph import Graph
from src.encoder import Encoder

from constants import TRIPLE_DIR, RESULT_DIR
from cli_args import SIZE, RATIO, THRESHOLD, OVERWRITE, MATCH, NAME


def main(size, ratio, threshold, overwrite, match, name):
    kg_dir = RESULT_DIR / (name or f"kg_nodes_ratio_{int(100 * ratio)}_threshold_{int(100 * threshold)}_{size}")
    kg_dir.mkdir(exist_ok=True)
    base_dir = kg_dir / "base"
    base_dir.mkdir(exist_ok=True)
    errors_dir = base_dir / "errors"
    errors_dir.mkdir(exist_ok=True)

    encoder = Encoder(size=size, ratio=ratio)

    failed_files = []
    files = [file for file in TRIPLE_DIR.glob(match) if file.suffix == ".csv" and (overwrite or not Path(BASE_DIR / f"{file.stem}.json").is_file())]
    sorted_files = sorted(files, key=lambda file: file.stat().st_size)
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