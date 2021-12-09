import numpy as np
import pandas as pd
import re
import argparse
import math

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--type", type=str, default="pira")
args = parser.parse_args()

TYPE = args.type

def read_pira():
    pira_df = pd.read_excel("data/pira.xlsx")
    article_ids = pira_df["eid_article_scopus"].unique()
    answers = pira_df[["eid_article_scopus", "answer_en_origin", "answer_en_validate"]]

    for article_id in article_ids:
        if not isinstance(article_id, str):
            article_answers = answers[answers["eid_article_scopus"].isna()]
        else:
            article_answers = answers[answers["eid_article_scopus"] == article_id]

        answer_couplets = []
        for _, answer in article_answers.iterrows():
            answer_couplet = answer["answer_en_origin"]
            if isinstance(answer["answer_en_validate"], str):
                answer_couplet += "\n" + answer["answer_en_validate"]
            answer_couplets.append(answer_couplet)

        with open(f"sentences/pira_{article_id}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(answer_couplets))


def read_abstracts():
    pira_df = pd.read_csv("data/abstracts.csv", sep=";")
    abstracts = pira_df["abstract"].unique()

    for i, abstract in enumerate(abstracts):
        clean_abstract = re.sub(r"</?[^>]+>", "", abstract) # Removes HTML tags
        with open(f"sentences/abstracts_{i}.txt", "w", encoding="utf-8") as f:
            f.write(clean_abstract)


def main():
    if TYPE == "abstracts":
        read_abstracts()
    elif TYPE == "pira":
        read_pira()

if __name__ == "__main__":
    main()