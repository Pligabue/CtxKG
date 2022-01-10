import pandas as pd


def get_article_id(group, no_id_counter):
    if i := group['eid_article_scopus'].first_valid_index():
        return group['eid_article_scopus'].loc[i], no_id_counter
    else:
        return f"no_id_{no_id_counter}", no_id_counter + 1
        
def main():
    pira_df = pd.read_excel("data/pira.xlsx")
    grouped_by_abstract = pira_df.groupby("abstract")
    no_id_counter = 0

    for abstract, group in grouped_by_abstract:
        article_id, no_id_counter = get_article_id(group, no_id_counter)

        with open(f"sentences/{article_id}_abstract.txt", "w", encoding="utf-8") as f:
            f.write(abstract)

        answers = [answer for _, row in group.iterrows() for answer in row[["answer_en_origin", "answer_en_validate"]] if type(answer) is str]
        with open(f"sentences/{article_id}_answers.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(answers))

        with open(f"sentences/{article_id}_combined.txt", "w", encoding="utf-8") as f:
            f.write(abstract + "\n" + "\n".join(answers))

if __name__ == "__main__":
    main()