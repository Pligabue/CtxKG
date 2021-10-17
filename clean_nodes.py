from pathlib import Path
import re
import json

def main():
    CURRENT_DIR = Path()
    dirs = [dir for dir in CURRENT_DIR.glob("kg_nodes*") if dir.is_dir()]

    for dir in dirs:
        nodes = {}
        for file in dir.glob("*.json"):
            with open(file) as f:
                nodes = json.load(f)

            with open(f"results/{dir.name}.summary.json", "w", encoding="utf-8") as f:
                json_string = json.dumps(nodes, indent=2)
                json_string = re.sub('\n {6}|\n {4}(?=\])', " ", json_string)
                json_string = re.sub('\[ ', "[", json_string)
                json_string = re.sub(' \]', "]", json_string)
                f.write(json_string)

if __name__ == "__main__":
    main()