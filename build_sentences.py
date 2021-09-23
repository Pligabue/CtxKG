import numpy as np
import pandas as pd
import re

def main():
    pira_c_df = pd.read_csv("./data/CSV/Pirá-C-Total.csv")
    pira_f_df = pd.read_csv("./data/CSV/Pirá-F-Total.csv")
    pira_t_df = pd.read_csv("./data/CSV/Pirá-T-Total.csv")
    pira_df = pd.concat([pira_c_df, pira_f_df, pira_t_df])

    dataset_df = pira_df[["eid_article_scopus", "answer_en_origin", "answer_en_validate"]]
    article_ids = dataset_df["eid_article_scopus"].unique()

    for article_id in article_ids:
        title = re.sub(r"\D", "_", article_id) if article_id is not np.nan else "others"
        sentences_df = dataset_df[dataset_df["eid_article_scopus"] == article_id]
        with open(f"sentences/{title}.txt", "w", encoding="utf-8") as f:
            origin_sentences = list(sentences_df["answer_en_origin"].dropna().unique())
            validate_sentences = list(sentences_df["answer_en_validate"].dropna().unique())
            all_sentences = [sentence for sentence in [*origin_sentences, *validate_sentences] if sentence]
            f.write("\n".join(all_sentences))

if __name__ == "__main__":
    main()