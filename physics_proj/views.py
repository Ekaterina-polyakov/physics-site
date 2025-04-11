"""
This file with functions wich renders pages
"""

import json
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse
import pandas as pd

from . import db_work


def index(request):
    """
    index view
    """
    return render(request, "index.html")


def terms_list(request):
    """
    terms list view
    """
    terms = db_work.get_terms_for_table()
    return render(request, "term_list.html", context={"terms": terms})


def add_term(request):
    """
    add term view
    """
    return render(request, "term_add.html")


def send_term(request):
    """
    send term view
    """
    if request.method == "POST":
        cache.clear()
        print(request.POST)
        data = pd.read_csv("data/terms.csv", delimiter=";")
        user_name = request.POST.get("name")
        new_term = request.POST.get("new_term", "").capitalize().strip()
        new_definition = (
            request.POST.get("new_definition", "")
            .replace(";", ",")
            .capitalize()
            .strip()
        )

        context = {"user": user_name}
        if len(new_definition) == 0:
            context["success"] = False
            context["comment"] = "Описание не должен быть пустым"
        elif len(new_term) == 0:
            context["success"] = False
            context["comment"] = "Формула не должно быть пустым"
        elif new_definition + new_term in (data["explanation"] + data["term"]).values:
            context["success"] = False
            context["comment"] = "Пара формула + описание должна быть уникальной"
        else:
            context["success"] = True
            context["comment"] = "Ваша формула принята"
            db_work.write_term(new_term, new_definition)
        if context["success"]:
            context["success-title"] = ""
        return render(request, "term_request.html", context)
    add_term(request)
    return None


def show_stats(request):
    """
    renders stats
    """
    stats = db_work.get_terms_stats()
    return render(request, "stats.html", stats)


def game_view(request):
    """
    renders game page
    """
    data = pd.read_csv("data/terms.csv", delimiter=";").sample(n=4)

    formulas = data["term"]
    explanations = data["explanation"]

    context = {
        "formulas": formulas,
        "explanations": explanations,
    }

    return render(request, "game_page.html", context)


def check_game_view(request):
    """
    renders page with game result
    """
    data = pd.read_csv("data/terms.csv", delimiter=";")
    word_pairs = {
        data.iloc[i]["term"]: data.iloc[i]["explanation"] for i in range(len(data))
    }
    if request.method == "POST":
        correct_answers = 0
        total_questions = 4
        results = []

        for i in range(1, 5):
            explanation_choice = request.POST.get(f"explanation_choice_{i}")
            formula = request.POST.get(f"formula_{i}")
            correct_formula = word_pairs[formula]
            is_correct = explanation_choice == correct_formula

            if is_correct:
                correct_answers += 1

            results.append(
                {
                    "formula": formula,
                    "chosen_explanation": explanation_choice,
                    "correct_explanation": correct_formula,
                    "is_correct": is_correct,
                }
            )

        percentage = (
            (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        )

        context = {
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "percentage": percentage,
            "results": results,
        }

        with open("data/games_stats.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        data["tries"] += 1
        if int(percentage) == 100:
            data["successes"] += 1

        with open("data/games_stats.json", "w", encoding="utf-8") as f:
            json.dump(data, f)

        return render(request, "results.html", context)
    return redirect(reverse("game"))
