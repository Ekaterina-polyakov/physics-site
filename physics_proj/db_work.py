"""
This module made for fuctions which works with database
"""

import json
import pandas as pd


def get_terms_for_table():
    """
    Get all terms from table
    """
    terms = []
    with open("./data/terms.csv", "r", encoding="utf-8") as f:
        cnt = 1
        for line in f.readlines()[1:]:
            term, definition, _ = line.split(";")
            terms.append([cnt, term, definition])
            cnt += 1
    return terms


def write_term(new_term, new_definition):
    """
    Writes new term
    """
    new_term_line = f"{new_term};{new_definition};user"
    with open("./data/terms.csv", "r", encoding="utf-8") as f:
        existing_terms = [l.strip("\n") for l in f.readlines()]
        title = existing_terms[0]
        old_terms = existing_terms[1:]
    terms_sorted = old_terms + [new_term_line]
    terms_sorted.sort()
    new_terms = [title] + terms_sorted
    with open("./data/terms.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(new_terms))


def get_terms_stats():
    """
    gets stats
    """
    terms_count = len(pd.read_csv("data/terms.csv"))

    with open("data/games_stats.json", "r", encoding="utf-8") as file:
        games_data = json.load(file)

    percentage = 0
    if games_data["tries"]:
        percentage = games_data["successes"] / games_data["tries"] * 100

    stats = {
        "terms_all": terms_count,
        "games_avg": games_data["tries"],
        "games_succes": games_data["successes"],
        "games_percentage": round(percentage, 1),
    }
    return stats
