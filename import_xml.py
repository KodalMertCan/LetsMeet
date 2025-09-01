#!/usr/bin/env python3
# import_xml.py – liest Lets_Meet_Hobbies.xml und befüllt USER/HOBBY/HOBBY_PRIORITY

from pathlib import Path
import psycopg2
from lxml import etree
from db_utils import PG_DSN, ensure_user, ensure_hobby

XML_PATH = Path("Lets_Meet_Hobbies.xml")

def run():
    if not XML_PATH.exists():
        print(f"[SKIP] XML fehlt: {XML_PATH}")
        return
    print(f"[OK] XML: {XML_PATH}")
    tree = etree.parse(str(XML_PATH))

    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            for u in tree.findall(".//user"):
                email = (u.findtext("email") or "").strip().lower()
                if not email:
                    continue
                # Name kann "Nachname, Vorname" oder frei sein – wir speichern ihn roh,
                # du kannst split_name importieren, wenn du willst.
                user_id = ensure_user(cur, email, surname=None, name=(u.findtext("name") or "").strip())
                for hobby in u.findall("hobby"):
                    hname = (hobby.text or "").strip()
                    if not hname:
                        continue
                    hid = ensure_hobby(cur, hname)
                    cur.execute(
                        "INSERT INTO HOBBY_PRIORITY (user_id, hobby_id, priority) VALUES (%s,%s,%s) "
                        "ON CONFLICT DO NOTHING",
                        (user_id, hid, "0")
                    )
        conn.commit()
    print("XML-Import abgeschlossen.")

if __name__ == "__main__":
    run()
