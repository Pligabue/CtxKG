import subprocess
import requests
from tqdm import tqdm
from zipfile import ZipFile, BadZipFile

from constants import OPEN_IE_DIR

def ask(question):
    response = input(question)
    if response in ["Y", "y", "yes", "Yes", "YES"]:
        return True
    return False

def check_stanford_lib_path():
    try:
        match = "stanford-corenlp-*[!.zip]"
        return next(OPEN_IE_DIR.glob(match))
    except StopIteration:
        return None

def check_stanford_lib_zip_path():
    try:
        match = "stanford-corenlp-*.zip"
        return next(OPEN_IE_DIR.glob(match))
    except StopIteration:
        return None

def unzip_stanford_lib():
    zip_path = check_stanford_lib_zip_path()
    if zip_path:
        try:
            with ZipFile(zip_path.absolute()) as zipped_lib:
                zipped_lib.extractall(OPEN_IE_DIR.absolute())
            if ask("Stanford's CoreNLP library successfully unzipped. Remove ZIP? [Y/n] "):
                zip_path.unlink(missing_ok=True)
        except BadZipFile:
            if ask("Stanford's CoreNLP library ZIP is incomplete. Do you want to delete it and try again? [Y/n] "):
                zip_path.unlink(missing_ok=True)
                download_stanford_lib_zip()
                unzip_stanford_lib()
    else:
        if ask("Stanford's CoreNLP library ZIP is missing. Do to try to download it again? [Y/n] "):
            download_stanford_lib_zip()
            unzip_stanford_lib()

def download_stanford_lib_zip():
    lib_download_url = "https://nlp.stanford.edu/software/stanford-corenlp-latest.zip"
    r = requests.get(lib_download_url, stream=True)
    if r.ok:
        print("Downloading...")
        content_length = int(r.headers["Content-Length"])
        zipped_lib_file = OPEN_IE_DIR / "stanford-corenlp-latest.zip"
        with open(zipped_lib_file, 'wb') as fd:
            with tqdm(total=content_length, unit="B", unit_scale=True, unit_divisor=1024) as pbar:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    fd.write(chunk)
                    pbar.update(len(chunk))
    else:
        print("Could not initiate download. Maybe something is wrong with your internet connection.")

def get_stanford_lib_path():
    stanford_lib_path = check_stanford_lib_path()
    if stanford_lib_path:
        return stanford_lib_path
    else:
        stanford_lib_zip_path = check_stanford_lib_zip_path()
        if stanford_lib_zip_path:
            unzip_stanford_lib()
            return check_stanford_lib_path()
        else:
            if ask("Stanford's CoreNLP library is missing. Do you want to download it? [Y/n] "):
                download_stanford_lib_zip()
                unzip_stanford_lib()
                return check_stanford_lib_path()
            else:
                return None

def build_triples():
    stanford_lib = get_stanford_lib_path()
    if stanford_lib:
        lib_full_path = stanford_lib.absolute() / "*"
        java_path = OPEN_IE_DIR / "*.java"
        try:
            subprocess.run(["javac", "-cp", lib_full_path, java_path], check=True)
            subprocess.run(["java", "-cp", f"{lib_full_path};. ", "-Dfile.encoding=UTF8", "openie.TripleBuilder"])
        except subprocess.CalledProcessError:
            print("Error compiling Java code.")
    else:
        print("Cannot continue. Stanford's CoreNLP library is missing.")


if __name__ == "__main__":
    build_triples()