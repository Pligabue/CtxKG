import subprocess

from .constants import OPEN_IE_DIR, OPEN_IE_JAR
from ...constants import DOCUMENT_DIR, TRIPLE_DIR


def setup_directories(reference_dir=DOCUMENT_DIR, target_dir=TRIPLE_DIR):
    subdirectories = [f for f in reference_dir.iterdir() if f.is_dir()]
    for subdir in subdirectories:
        target_subdir = target_dir / subdir.name
        target_subdir.mkdir(exist_ok=True)
        setup_directories(subdir, target_subdir)


def build_triples():
    setup_directories()
    try:
        if not OPEN_IE_JAR.exists():
            subprocess.run(["mvn", "compile", "assembly:single"], cwd=OPEN_IE_DIR, shell=True, check=True)
        subprocess.run(["java", "-cp", str(OPEN_IE_JAR), "com.triplebuilder.app.TripleBuilder"])
    except subprocess.CalledProcessError:
        print("Error compiling Java code.")


if __name__ == "__main__":
    build_triples()
