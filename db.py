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


if __name__ == "__main__":
    rows = query_all(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )
    for (name,) in rows:
        print(name)

