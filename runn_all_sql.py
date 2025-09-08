# run_all_sql.py – Python-only SQL Runner
import psycopg2
from psycopg2 import OperationalError
from db_utils import PG_DSN
import import_excel_script, import_xml, import_mongo

def run_sql():
    print("[OK] SQL-Schema einspielen (Python)")
    with open("create_tables.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    try:
        with psycopg2.connect(PG_DSN) as conn:
            with conn.cursor() as cur:
                for stmt in statements:
                    cur.execute(stmt)
            conn.commit()
        print("SQL-Schema erfolgreich ausgeführt.")
    except OperationalError as e:
        print("❌ Konnte keine Verbindung zu Postgres aufbauen.")
        print("   Prüfe Host/Port/User/Passwort/DB oder starte den Container.")
        print(f"   Aktueller DSN: {PG_DSN}")
        raise

if __name__ == "__main__":
    run_sql()
    import_excel_script.run()
    import_xml.run()
    import_mongo.run()
    print("Alles abgeschlossen.")

