# db_utils.py
# Gemeinsame Helfer + DB-Konfiguration (Postgres) für alle Importe.

from datetime import datetime, date
from dateutil import parser as dateparser
import pandas as pd

PG_DSN = "dbname=lf8_lets_meet_db user=user password=secret host=localhost port=5432"

def to_date(raw):
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
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
