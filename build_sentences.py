import numpy as np
import pandas as pd
import re

def main():
    pira_df = pd.read_csv("data/pira.csv", sep=";")
    abstracts = pira_df["abstract"].unique()

    for i, abstract in enumerate(abstracts):
        with open(f"sentences/abstract_{i}.txt", "w", encoding="utf-8") as f:
            clean_abstract = re.sub(r"</?[^>]+>", "", abstract) # Removes HTML tags
            f.write(clean_abstract)

if __name__ == "__main__":
    main()