from __future__ import annotations

from db import (
    add_category,
    add_question,
    add_question_to_test,
    get_category_name,
    get_or_create_test,
    list_categories,
    list_questions_by_category,
    list_test_questions,
    list_tests,
)
from cli_ui import parse_id_list, prompt


def show_categories() -> None:
    cats = list_categories()
    if not cats:
        print("Keine Kategorien vorhanden.")
        return
    print("\nKategorien:")
    for cid, name in cats:
        print(f"  {cid}: {name}")


def create_category() -> None:
    name = prompt("Neuer Kategoriename: ")
    if not name:
        print("Abbruch: leerer Name.")
        return
    cid = add_category(name)
    print(f"✅ Kategorie '{name}' hat ID: {cid}")


def choose_category_id() -> int | None:
    cats = list_categories()
    if not cats:
        print("Keine Kategorien vorhanden.")
        return None

    show_categories()
    valid = {cid for cid, _ in cats}

    while True:
        raw = prompt("Kategorie-ID (leer = Abbruch): ")
        if raw == "":
            return None
        if raw.isdigit():
            cid = int(raw)
            if cid in valid:
                return cid
        print("Ungültige Kategorie-ID.")


def show_questions_in_category() -> None:
    cid = choose_category_id()
    if cid is None:
        return

    name = get_category_name(cid) or f"ID {cid}"
    qs = list_questions_by_category(cid)

    print(f"\nFragen in Kategorie '{name}':")
    if not qs:
        print("  (keine)")
        return

    for qid, text in qs:
        print(f"  {qid}: {text}")


def create_question() -> None:
    cid = choose_category_id()
    if cid is None:
        return

    qtext = prompt("Fragetext: ")
    if not qtext:
        print("Abbruch: leerer Fragetext.")
        return

    sol = prompt("Lösung (optional, leer ok): ")
    qid = add_question(qtext, sol, cid)
    print(f"✅ Frage hat ID: {qid}")


def choose_or_create_test_id() -> int | None:
    tests = list_tests()
    if tests:
        print("\nVorhandene Tests (neueste zuerst):")
        for tid, title, date in tests[:10]:
            d = date if date else "-"
            print(f"  {tid}: {title} ({d})")
        print("  0: Neu anlegen / bestehenden per Titel+Datum holen")
    else:
        print("\nNoch keine Tests vorhanden. Wir legen einen an.")

    raw = prompt("Test-ID wählen (0 oder leer=Abbruch): ")
    if raw == "":
        return None
    if not raw.isdigit():
        print("Ungültige Eingabe.")
        return None

    choice = int(raw)

    if choice != 0:
        valid_ids = {tid for tid, _, _ in tests}
        if choice in valid_ids:
            return choice
        print("Diese Test-ID gibt es nicht.")
        return None

    title = prompt("Testtitel: ")
    if not title:
        print("Abbruch: leerer Titel.")
        return None
    date = prompt("Testdatum (YYYY-MM-DD, optional): ") or None
    return get_or_create_test(title, date)


def add_questions_to_test() -> None:
    cid = choose_category_id()
    if cid is None:
        return

    qs = list_questions_by_category(cid)
    if not qs:
        print("Keine Fragen in dieser Kategorie.")
        return

    print("\nFragen:")
    for qid, text in qs:
        print(f"  {qid}: {text}")

    raw = prompt("\nFrage-IDs eingeben (z.B. 1 3 5) oder leer=Abbruch: ")
    if raw == "":
        return
    qids = parse_id_list(raw)
    if not qids:
        print("Keine gültigen IDs.")
        return

    test_id = choose_or_create_test_id()
    if test_id is None:
        return

    for qid in qids:
        add_question_to_test(test_id, qid)

    print(f"✅ Fragen zu Test-ID {test_id} hinzugefügt.")


def show_test() -> None:
    tests = list_tests()
    if not tests:
        print("Keine Tests vorhanden.")
        return

    print("\nTests:")
    for tid, title, date in tests[:20]:
        d = date if date else "-"
        print(f"  {tid}: {title} ({d})")

    raw = prompt("Test-ID anzeigen (leer=Abbruch): ")
    if raw == "":
        return
    if not raw.isdigit():
        print("Ungültige Eingabe.")
        return

    test_id = int(raw)
    items = list_test_questions(test_id)
    if not items:
        print("Keine Fragen in diesem Test (oder Test-ID ungültig).")
        return

    print("\nFragen im Test:")
    for qid, text, solution in items:
        print(f"  {qid}: {text}")
        # print(f"     Lösung: {solution}")  # optional

