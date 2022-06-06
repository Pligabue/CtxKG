from pathlib import Path

from src.graph import Graph
from cli_args import MATCH


def main(match):
    RESULTS_PATH = Path("./results")
    dirs = [dir for dir in RESULTS_PATH.glob(match) if dir.is_dir()]

    for dir in dirs:
        BASE_DIR = dir / "base"
        CLEAN_DIR = dir / "clean"
        CLEAN_DIR.mkdir(exist_ok=True)
        
        for file in BASE_DIR.glob("*.json"):
            graph = Graph.from_json(file)
            graph.clean()
            graph.save_json(CLEAN_DIR / file.name)

if __name__ == "__main__":
    main(MATCH)