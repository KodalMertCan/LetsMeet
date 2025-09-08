#!/usr/bin/env python3
# Vereinfachte Migration für Let's Meet – angepasst an ERD:
# - USER_LIKE: like_id PK, sender_id, receiver_id, timestamp, status
# - PHOTO: link TEXT, created_at DATE
# Liest Excel (Lets_Meet_DB_Dump.xlsx), XML (Lets_Meet_Hobbies.xml) und MongoDB.

from datetime import datetime, date
from dateutil import parser as dateparser
from pathlib import Path
import re
import pandas as pd
import psycopg2
from pymongo import MongoClient
from lxml import etree

# ===================== Konfiguration =====================
PG_DSN = "dbname=lf8_lets_meet_db user=user password=secret host=localhost port=5432"

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "LetsMeet"
MONGO_USERS_COLLECTION = "users"

EXCEL_PATH = Path("Lets_Meet_DB_Dump.xlsx")
XML_PATH   = Path("Lets_Meet_Hobbies.xml")
# =========================================================

# ---------------- Hilfsfunktionen ----------------
def to_date(raw):
    if not raw or pd.isna(raw):
        return None
    if isinstance(raw, (datetime, date)):
        return raw.date() if isinstance(raw, datetime) else raw
    try:
        return dateparser.parse(str(raw), dayfirst=True).date()
    except Exception:
        return None

def split_name(raw):
    if not raw or not isinstance(raw, str):
        return None, None
    parts = [p.strip() for p in raw.split(",")]
    return (parts[0], parts[1]) if len(parts) == 2 else (None, raw.strip())

def parse_address(raw):
    if not raw or not isinstance(raw, str):
        return None, None, None, None
    try:
        streetnr, plz, city = [p.strip() for p in raw.split(",", 2)]
    except ValueError:
        return None, None, None, None
    street, number = (streetnr.rsplit(" ", 1) if " " in streetnr else (streetnr, None))
    return street, number, plz, city

def parse_hobbies(raw):
    if not raw or not isinstance(raw, str):
        return []
    hobbies = []
    pattern = re.compile(r"""
        ^(.*?)                     # Hobbyname
        (?:\s*%\s*(-?\d+)\s*%\s*)?$   # optionale %Priorität%
    """, re.VERBOSE)
    for chunk in raw.split(";"):
        m = pattern.match(chunk.strip())
        if m:
            hobbies.append((m.group(1).strip(), m.group(2)))
    return hobbies

# ---------------- DB-Helfer ----------------
def ensure_user(cur, email, surname=None, name=None,
                gender=None, gender_interest=None, birthdate=None,
                phone=None, street=None, number=None, zip_code=None, city=None,
                created_at=None, updated_at=None):
    cur.execute(
        """
        INSERT INTO "USER" (email, surname, name, gender, birthdate,
                            gender_interest, phone_number, street, number, zip, city,
                            created_at, updated_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                COALESCE(%s,CURRENT_DATE), COALESCE(%s,CURRENT_DATE))
        ON CONFLICT (email) DO UPDATE SET
          surname=COALESCE(EXCLUDED.surname, "USER".surname),
          name=COALESCE(EXCLUDED.name, "USER".name),
          gender=COALESCE(EXCLUDED.gender, "USER".gender),
          birthdate=COALESCE(EXCLUDED.birthdate, "USER".birthdate),
          gender_interest=COALESCE(EXCLUDED.gender_interest, "USER".gender_interest),
          phone_number=COALESCE(EXCLUDED.phone_number, "USER".phone_number),
          street=COALESCE(EXCLUDED.street, "USER".street),
          number=COALESCE(EXCLUDED.number, "USER".number),
          zip=COALESCE(EXCLUDED.zip, "USER".zip),
          city=COALESCE(EXCLUDED.city, "USER".city),
          updated_at=CURRENT_DATE
        RETURNING id
        """,
        (email, surname, name, gender, birthdate, gender_interest,
         phone, street, number, zip_code, city, created_at, updated_at)
    )
    return cur.fetchone()[0]

def ensure_hobby(cur, name):
    cur.execute(
        "INSERT INTO HOBBY (hobby_name) VALUES (%s) "
        "ON CONFLICT (hobby_name) DO UPDATE SET hobby_name=EXCLUDED.hobby_name "
        "RETURNING hobby_id",
        (name,)
    )
    return cur.fetchone()[0]

def set_hobby_priority(cur, user_id, hobby_id, prio):
    prio = prio if prio is not None else "0"
    cur.execute(
        "INSERT INTO HOBBY_PRIORITY (user_id, hobby_id, priority) VALUES (%s,%s,%s) "
        "ON CONFLICT (user_id, hobby_id) DO UPDATE SET priority=EXCLUDED.priority",
        (user_id, hobby_id, prio)
    )

# ---------------- Importer ----------------
def import_excel(cur):
    if not EXCEL_PATH.exists():
        print(f"[SKIP] Excel fehlt: {EXCEL_PATH}")
        return
    print(f"[OK] Excel: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH)
    # [Nachname, Vorname] | [Straße Nr, PLZ, Ort] | Telefon | Hobbies | E-Mail | Geschlecht | Interessiert an | Geburtsdatum
    for _, row in df.iterrows():
        surname, name = split_name(row.iloc[0])
        street, number, plz, city = parse_address(row.iloc[1])
        user_id = ensure_user(
            cur,
            email=str(row.iloc[4]).strip().lower(),
            surname=surname, name=name,
            gender=row.iloc[5], gender_interest=row.iloc[6],
            birthdate=to_date(row.iloc[7]),
            phone=str(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
            street=street, number=number, zip_code=plz, city=city
        )
        for hobby_name, prio in parse_hobbies(row.iloc[3]):
            if hobby_name:
                hid = ensure_hobby(cur, hobby_name)
                set_hobby_priority(cur, user_id, hid, prio)

def import_xml(cur):
    if not XML_PATH.exists():
        print(f"[SKIP] XML fehlt: {XML_PATH}")
        return
    print(f"[OK] XML: {XML_PATH}")
    tree = etree.parse(str(XML_PATH))
    for u in tree.findall(".//user"):
        email = (u.findtext("email") or "").strip().lower()
        if not email:
            continue
        surname, name = split_name(u.findtext("name") or "")
        user_id = ensure_user(cur, email, surname, name)
        for hobby in u.findall("hobby"):
            hname = (hobby.text or "").strip()
            if hname:
                hid = ensure_hobby(cur, hname)
                cur.execute(
                    "INSERT INTO HOBBY_PRIORITY (user_id, hobby_id, priority) VALUES (%s,%s,%s) "
                    "ON CONFLICT DO NOTHING",
                    (user_id, hid, "0")
                )

def import_mongo(cur):
    print("[OK] MongoDB")
    client = MongoClient(MONGO_URI)
    coll = client[MONGO_DB][MONGO_USERS_COLLECTION]
    for doc in coll.find({}):
        email = str(doc.get("_id")).lower()
        surname, name = split_name(doc.get("name", ""))
        user_id = ensure_user(
            cur, email, surname, name,
            phone=doc.get("phone"),
            created_at=to_date(doc.get("createdAt")),
            updated_at=to_date(doc.get("updatedAt"))
        )
        # Friends
        for f in doc.get("friends", []):
            fid = ensure_user(cur, str(f).lower())
            cur.execute(
                "INSERT INTO FRIEND_LIST (user_id, friend_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                (user_id, fid)
            )
        # Likes  (angepasst: USER_LIKE hat status & timestamp, KEINE conversation_id/text)
        for like in doc.get("likes", []):
            rid = ensure_user(cur, str(like.get("liked_email")).lower())
            cur.execute(
                "INSERT INTO USER_LIKE (sender_id, receiver_id, timestamp, status) "
                "VALUES (%s,%s,%s,%s)",
                (user_id, rid, to_date(like.get("timestamp")), like.get("status"))
            )
        # Messages (unverändert)
        for msg in doc.get("messages", []):
            recv = str(msg.get("receiver_email")).lower()
            ensure_user(cur, recv)
            cur.execute(
                "INSERT INTO NACHRICHT (user_id, conversation_id, receiver_email, text, timestamp) "
                "VALUES (%s,%s,%s,%s,%s)",
                (user_id, msg.get("conversation_id"), recv, msg.get("message"), to_date(msg.get("timestamp")))
            )
    client.close()

# ---------------- Orchestrierung ----------------
def run_migration():
    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            import_excel(cur)
            import_xml(cur)
            import_mongo(cur)
        conn.commit()
    print("Migration abgeschlossen.")

if __name__ == "__main__":
    run_migration()
