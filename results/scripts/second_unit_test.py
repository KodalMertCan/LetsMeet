import os
import unittest
import psycopg2

PG_DSN = os.getenv(
    "PG_DSN",
    "dbname=lf8_lets_meet_db user=user password=secret host=localhost port=5432"
)
TARGET_EMAIL = os.getenv("TARGET_EMAIL", "karl-heinz.fink@ge-em-ix.kom").strip().lower()  # MUSS gesetzt sein!


def pg_conn():
    return psycopg2.connect(PG_DSN)


def pretty_list(items):
    return ", ".join(filter(None, items)) if items else "—"


class TestDBModelUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not TARGET_EMAIL:
            raise unittest.SkipTest("TARGET_EMAIL ist nicht gesetzt. Beispiel: export TARGET_EMAIL=john@example.com")
        cls.conn = pg_conn()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.conn.close()
        except Exception:
            pass

    def test_user_with_hobbies_likes_msgs(self):
        sql = """
        SELECT
          u.id, u.email, u.name, u.surname, u.city,

          COALESCE(hh.hobbies, ARRAY[]::text[])   AS hobbies,

          COALESCE(ls.sent_to,  ARRAY[]::text[])  AS likes_sent_to,
          COALESCE(lr.recv_from,ARRAY[]::text[])  AS likes_received_from,

          COALESCE(ms.sent_to,  ARRAY[]::text[])  AS msgs_sent_to,
          COALESCE(mr.recv_from,ARRAY[]::text[])  AS msgs_received_from

        FROM "USER" u

        -- Hobbies
        LEFT JOIN LATERAL (
          SELECT array_agg(DISTINCT h.hobby_name) AS hobbies
          FROM hobby_priority hp
          JOIN hobby h ON h.hobby_id = hp.hobby_id
          WHERE hp.user_id = u.id
        ) hh ON TRUE

        -- Likes gesendet
        LEFT JOIN LATERAL (
          SELECT array_agg(DISTINCT ur.email) AS sent_to
          FROM user_like l
          JOIN "USER" ur ON ur.id = l.receiver_id
          WHERE l.sender_id = u.id
        ) ls ON TRUE

        -- Likes empfangen
        LEFT JOIN LATERAL (
          SELECT array_agg(DISTINCT us.email) AS recv_from
          FROM user_like l
          JOIN "USER" us ON us.id = l.sender_id
          WHERE l.receiver_id = u.id
        ) lr ON TRUE

        -- Nachrichten gesendet
        LEFT JOIN LATERAL (
          SELECT array_agg(DISTINCT n.receiver_email) AS sent_to
          FROM nachricht n
          WHERE n.user_id = u.id
        ) ms ON TRUE

        -- Nachrichten empfangen
        LEFT JOIN LATERAL (
          SELECT array_agg(DISTINCT us.email) AS recv_from
          FROM nachricht n
          JOIN "USER" us ON us.id = n.user_id
          WHERE n.receiver_email = u.email
        ) mr ON TRUE

        WHERE u.email = %s;
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (TARGET_EMAIL,))
            row = cur.fetchone()

        self.assertIsNotNone(row, f"User {TARGET_EMAIL} nicht gefunden.")

        (user_id, email, name, surname, city,
         hobbies, likes_sent, likes_recv, msgs_sent, msgs_recv) = row

        # Ausgabe
        print("\n============================")
        print(f" Ergebnisse für Nutzer: {email}")
        print("============================")
        print(f"[USER] id={user_id}, name={name or ''} {surname or ''}, city={city or '—'}")
        print(f"[HOBBIES]           {pretty_list(hobbies)}")
        print(f"[LIKES  sent → ]    {pretty_list(likes_sent)}")
        print(f"[LIKES  ← recv]     {pretty_list(likes_recv)}")
        print(f"[MSG    sent → ]    {pretty_list(msgs_sent)}")
        print(f"[MSG    ← recv]     {pretty_list(msgs_recv)}")

        # Assertions
        self.assertEqual(email, TARGET_EMAIL)
        for arr in (hobbies, likes_sent, likes_recv, msgs_sent, msgs_recv):
            self.assertIsInstance(arr, list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
