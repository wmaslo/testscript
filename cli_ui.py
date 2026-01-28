from __future__ import annotations


def prompt(prompt_text: str) -> str:
    return input(prompt_text).strip()


def prompt_int(prompt_text: str) -> int:
    while True:
        raw = prompt(prompt_text)
        if raw.isdigit():
            return int(raw)
        print("Bitte eine Zahl eingeben.")


def parse_id_list(raw: str) -> list[int]:
    """
    Akzeptiert: '1 3 5' oder '1,3,5' oder gemischt.
    Entfernt Duplikate, behält Reihenfolge.
    """
    raw = raw.replace(",", " ")
    ids: list[int] = []
    for part in raw.split():
        if part.isdigit():
            ids.append(int(part))

    seen = set()
    out: list[int] = []
    for x in ids:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

