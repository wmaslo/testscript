PRAGMA foreign_keys = ON;

-- Kategorien
CREATE TABLE IF NOT EXISTS categories (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL UNIQUE
);

-- Fragen
CREATE TABLE IF NOT EXISTS questions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  question_text TEXT NOT NULL,
  solution      TEXT NOT NULL,
  category_id   INTEGER NOT NULL,
  FOREIGN KEY (category_id) REFERENCES categories(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

-- Tests
CREATE TABLE IF NOT EXISTS tests (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  title         TEXT NOT NULL,
  test_date     TEXT NOT NULL  -- ISO: YYYY-MM-DD
);

-- Zuordnung Test ↔ Fragen (N:M)
CREATE TABLE IF NOT EXISTS test_questions (
  test_id       INTEGER NOT NULL,
  question_id   INTEGER NOT NULL,
  PRIMARY KEY (test_id, question_id),
  FOREIGN KEY (test_id) REFERENCES tests(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY (question_id) REFERENCES questions(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

-- Optional, aber hilfreich für Performance:
CREATE INDEX IF NOT EXISTS idx_questions_category_id ON questions(category_id);
CREATE INDEX IF NOT EXISTS idx_test_questions_question_id ON test_questions(question_id);

