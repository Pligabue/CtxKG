from pathlib import Path
import json

def main():
    CURRENT_DIR = Path()
    dirs = [dir for dir in CURRENT_DIR.glob("kg_nodes*") if dir.is_dir()]

    for dir in dirs:
        nodes = {}
        for file in dir.glob("*.json"):
            with open(file) as f:
                nodes[file.stem] = json.load(f)

        with open(f"results/{dir.name}.summary.json", "w", encoding="utf-8") as f:
            json.dump(nodes, f, indent=2)

if __name__ == "__main__":
    main()