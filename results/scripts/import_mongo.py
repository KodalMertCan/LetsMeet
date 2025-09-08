#!/usr/bin/env python3
# import_mongo.py – liest Mongo (LetsMeet.users) und befüllt USER, FRIEND_LIST, USER_LIKE, NACHRICHT

import psycopg2
from pymongo import MongoClient
from db_utils import PG_DSN, to_date, split_name, ensure_user

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "LetsMeet"
MONGO_USERS_COLLECTION = "users"

def run():
    print("[OK] MongoDB")
    client = MongoClient(MONGO_URI)
    coll = client[MONGO_DB][MONGO_USERS_COLLECTION]

    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
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
                # Likes → USER_LIKE (like_id auto, status & timestamp)
                for like in doc.get("likes", []):
                    rid = ensure_user(cur, str(like.get("liked_email")).lower())
                    cur.execute(
                        "INSERT INTO USER_LIKE (sender_id, receiver_id, timestamp, status) VALUES (%s,%s,%s,%s)",
                        (user_id, rid, to_date(like.get("timestamp")), like.get("status"))
                    )
                # Messages → NACHRICHT
                for msg in doc.get("messages", []):
                    recv = str(msg.get("receiver_email")).lower()
                    ensure_user(cur, recv)
                    cur.execute(
                        "INSERT INTO NACHRICHT (user_id, conversation_id, receiver_email, text, timestamp) "
                        "VALUES (%s,%s,%s,%s,%s)",
                        (user_id, msg.get("conversation_id"), recv, msg.get("message"), to_date(msg.get("timestamp")))
                    )
        conn.commit()
    client.close()
    print("Mongo-Import abgeschlossen.")

if __name__ == "__main__":
    run()
