import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


# Standard: DB liegt im Projektroot
DEFAULT_DB_PATH = Path(__file__).with_name("datenbank.db")


def get_db_path() -> Path:
    """
    Erlaubt Override per Environment-Variable:
      TESTGEN_DB=/pfad/zur/db.db python main.py
    """
    return Path(os.getenv("TESTGEN_DB", DEFAULT_DB_PATH))


if not get_db_path().exists():
    raise RuntimeError(
        f"Datenbank fehlt: {get_db_path()}\n"
        "Hast du schema.sql angewendet?"
    )


@contextmanager
def connect():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    try:
        # SQLite: Foreign Keys müssen pro Verbindung aktiviert werden
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query_all(sql: str, params=()):
    with connect() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall()


def execute(sql: str, params=()):
    with connect() as conn:
        conn.execute(sql, params)


def add_category(name: str) -> int:
    """
    Legt eine Kategorie an und gibt die neue ID zurück.
    Falls der Name schon existiert (UNIQUE), wird die bestehende ID zurückgegeben.
    """
    name = name.strip()
    if not name:
        raise ValueError("Kategorie-Name darf nicht leer sein.")

    with connect() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO categories (name) VALUES (?);",
                (name,),
            )
            return int(cur.lastrowid)
        except sqlite3.IntegrityError:
            # z.B. UNIQUE-Constraint: Name existiert schon
            cur = conn.execute(
                "SELECT id FROM categories WHERE name = ?;",
                (name,),
            )
            row = cur.fetchone()
            # row sollte existieren, wenn UNIQUE der Grund war
            return int(row[0])


def list_categories() -> list[tuple[int, str]]:
    """
    Gibt alle Kategorien als Liste von (id, name) zurück.
    """
    rows = query_all("SELECT id, name FROM categories ORDER BY name;")
    return [(int(r[0]), str(r[1])) for r in rows]

def add_question(question_text: str, solution: str, category_id: int) -> int:
    """
    Legt eine Frage an und gibt die ID zurück.
    Wenn dieselbe Frage (Text + Kategorie) schon existiert, wird deren ID zurückgegeben.
    """
    question_text = question_text.strip()
    solution = solution.strip()

    if not question_text:
        raise ValueError("Fragetext darf nicht leer sein.")
    if category_id <= 0:
        raise ValueError("category_id muss > 0 sein.")

    with connect() as conn:
        # 1) existiert schon?
        cur = conn.execute(
            """
            SELECT id
            FROM questions
            WHERE category_id = ? AND question_text = ?
            LIMIT 1;
            """,
            (category_id, question_text),
        )
        row = cur.fetchone()
        if row:
            return int(row[0])

        # 2) sonst neu anlegen
        cur = conn.execute(
            """
            INSERT INTO questions (question_text, solution, category_id)
            VALUES (?, ?, ?);
            """,
            (question_text, solution, category_id),
        )
        return int(cur.lastrowid)


def list_questions_by_category(category_id: int) -> list[tuple[int, str]]:
    """
    Gibt Fragen einer Kategorie als Liste von (id, question_text) zurück.
    """
    rows = query_all(
        """
        SELECT id, question_text
        FROM questions
        WHERE category_id = ?
        ORDER BY id;
        """,
        (category_id,),
    )
    return [(int(r[0]), str(r[1])) for r in rows]

def get_or_create_test(title: str, test_date: str | None = None) -> int:
    """
    Holt einen bestehenden Test (title + test_date) oder legt ihn neu an.
    Gibt test_id zurück.
    """
    title = title.strip()
    if not title:
        raise ValueError("Titel darf nicht leer sein.")

    with connect() as conn:
        cur = conn.execute(
            """
            SELECT id
            FROM tests
            WHERE title = ? AND test_date IS ?
            LIMIT 1;
            """,
            (title, test_date),
        )
        row = cur.fetchone()
        if row:
            return int(row[0])

        cur = conn.execute(
            "INSERT INTO tests (title, test_date) VALUES (?, ?);",
            (title, test_date),
        )
        return int(cur.lastrowid)


def add_question_to_test(test_id: int, question_id: int) -> None:
    """
    Verknüpft eine Frage mit einem Test (m:n).
    Falls schon vorhanden, passiert nichts.
    """
    if test_id <= 0 or question_id <= 0:
        raise ValueError("test_id und question_id müssen > 0 sein.")

    with connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO test_questions (test_id, question_id) VALUES (?, ?);",
            (test_id, question_id),
        )


def list_test_questions(test_id: int) -> list[tuple[int, str, str]]:
    """
    Gibt alle Fragen eines Tests zurück:
    (question_id, question_text, solution)
    """
    rows = query_all(
        """
        SELECT q.id, q.question_text, q.solution
        FROM test_questions tq
        JOIN questions q ON q.id = tq.question_id
        WHERE tq.test_id = ?
        ORDER BY q.id;
        """,
        (test_id,),
    )
    return [(int(r[0]), str(r[1]), str(r[2])) for r in rows]

def list_tests() -> list[tuple[int, str, str | None]]:
    """
    Gibt alle Tests zurück als (id, title, test_date).
    Neueste zuerst (nach id).
    """
    rows = query_all(
        "SELECT id, title, test_date FROM tests ORDER BY id DESC;"
    )
    return [(int(r[0]), str(r[1]), r[2] if r[2] is None else str(r[2])) for r in rows]


def get_category_name(category_id: int) -> str | None:
    row = query_all(
        "SELECT name FROM categories WHERE id = ? LIMIT 1;",
        (category_id,),
    )
    if not row:
        return None
    return str(row[0][0])


def question_exists(question_id: int) -> bool:
    rows = query_all(
        "SELECT 1 FROM questions WHERE id = ? LIMIT 1;",
        (question_id,),
    )
    return bool(rows)


if __name__ == "__main__":
    cat_id = add_category("Grundlagen")
    print(f"Kategorie 'Grundlagen' hat ID: {cat_id}")

    # Beispiel-Frage anlegen
    q_id = add_question(
        "Was ist SQLite?",
        "Eine dateibasierte relationale Datenbank, die in einer einzelnen Datei gespeichert wird.",
        cat_id,
    )
    print(f"Neue Frage hat ID: {q_id}")

    # Kategorien ausgeben
    for cid, name in list_categories():
        print(f"{cid}: {name}")

    # Fragen der Kategorie ausgeben
    print("\nFragen in 'Grundlagen':")
    for qid, text in list_questions_by_category(cat_id):
        print(f"{qid}: {text}")

    # Test erstellen
    test_id = get_or_create_test("Test 1 - Grundlagen", "2026-01-28")
    print(f"\nNeuer Test hat ID: {test_id}")

    # Frage(n) dem Test hinzufügen
    add_question_to_test(test_id, q_id)

    # Testfragen anzeigen
    print("\nFragen im Test:")
    for qid, text, sol in list_test_questions(test_id):
        print(f"{qid}: {text}")
        print(f"   Lösung: {sol}")

