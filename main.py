from __future__ import annotations

from actions import (
    add_questions_to_test,
    create_category,
    create_question,
    show_categories,
    show_questions_in_category,
    show_test,
)
from cli_ui import prompt


def menu() -> int:
    print(
        "\n=== Testgenerator (CLI) ===\n"
        "1) Kategorien anzeigen\n"
        "2) Kategorie anlegen\n"
        "3) Fragen einer Kategorie anzeigen\n"
        "4) Frage anlegen\n"
        "5) Test erstellen/auswählen & Fragen hinzufügen\n"
        "6) Test anzeigen\n"
        "0) Ende\n"
    )
    choice = prompt("Auswahl: ")
    return int(choice) if choice.isdigit() else -1


def main() -> None:
    actions = {
        1: show_categories,
        2: create_category,
        3: show_questions_in_category,
        4: create_question,
        5: add_questions_to_test,
        6: show_test,
    }

    while True:
        choice = menu()
        if choice == 0:
            print("Tschüss.")
            return

        action = actions.get(choice)
        if not action:
            print("Ungültige Auswahl.")
            continue

        action()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAbbruch (Ctrl+C).")

