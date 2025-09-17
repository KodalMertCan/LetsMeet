#!/usr/bin/env python3
# import_excel.py – liest Lets_Meet_DB_Dump.xlsx und befüllt USER/HOBBY/HOBBY_PRIORITY

from pathlib import Path
import re
import pandas as pd
import psycopg2
from db_connection_script import PG_DSN, to_date, split_name, ensure_user, ensure_hobby, set_hobby_priority

EXCEL_PATH = Path("/workspaces/LetsMeet/Lets_Meet_DB_Dump.xlsx")

# "Hobby %prio%; Hobby2 %prio%"
HOBBY_RE = re.compile(r"""
    ^(.*?)                 # Hobbyname
    (?:\s*%\s*(-?\d+)\s*%\s*)?$   # optionale %Priorität%
""", re.VERBOSE)

def parse_address(raw: str):
    if not raw or not isinstance(raw, str):
        return None, None, None, None
    try:
        streetnr, plz, city = [p.strip() for p in raw.split(",", 2)]
    except ValueError:
        return None, None, None, None
    street, number = (streetnr.rsplit(" ", 1) if " " in streetnr else (streetnr, None))
    return street, number, plz, city

def parse_hobbies(raw: str):
    if not raw or not isinstance(raw, str):
        return []
    out = []
    for chunk in raw.split(";"):
        m = HOBBY_RE.match(chunk.strip())
        if m:
            out.append((m.group(1).strip(), m.group(2)))
    return out

def run():
    if not EXCEL_PATH.exists():
        print(f"[SKIP] Excel fehlt: {EXCEL_PATH}")
        return
    print(f"[OK] Excel: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH)

    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            # Spaltenreihenfolge laut Aufgabe:
            # 0:[Nachname, Vorname] 1:[Straße Nr, PLZ, Ort] 2:Telefon 3:Hobbies
            # 4:E-Mail 5:Geschlecht 6:Interessiert an 7:Geburtsdatum
            for _, row in df.iterrows():
                surname, name = split_name(row.iloc[0])
                street, number, plz, city = parse_address(row.iloc[1])
                email = str(row.iloc[4]).strip().lower()
                user_id = ensure_user(
                    cur,
                    email=email,
                    surname=surname,
                    name=name,
                    gender=row.iloc[5],
                    gender_interest=row.iloc[6],
                    birthdate=to_date(row.iloc[7]),
                    phone=str(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
                    street=street, number=number, zip_code=plz, city=city
                )
                for hobby_name, prio in parse_hobbies(row.iloc[3]):
                    if hobby_name:
                        hid = ensure_hobby(cur, hobby_name)
                        set_hobby_priority(cur, user_id, hid, prio)
        conn.commit()
    print("Excel-Import abgeschlossen.")

if __name__ == "__main__":
    run()
