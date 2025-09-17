import unittest
from datetime import date
import import_excel_script as excel_mod
import import_xml_script as xml_mod
import import_mongo_script as mongo_mod


# =============== Excel: 3 Beispieldatensätze ===============
class TestExcelExamples(unittest.TestCase):
    def test_excel_three_rows(self):
        rows = [
            ["Doe, John", "Musterstraße 12, 28199, Bremen", "0421/123",
             "Gaming %5%; Chess", "john@example.com", "m", "f", "01.02.2000"],
            ["Müller, Anna", "Hauptweg 5, 12345, Berlin", "030/987",
             "Lesen %10%; Kochen", "anna@example.com", "w", "m", "1995-05-15"],
            ["Ali", "Bahnhofstr 7, 67890, Köln", None,
             "Fußball; Reisen %-3%", "ali@example.com", "m", "w", ""],
        ]
        for i, r in enumerate(rows, start=1):
            surname, name = excel_mod.split_name(r[0])
            street, number, plz, city = excel_mod.parse_address(r[1])
            hobbies = excel_mod.parse_hobbies(r[3])
            bday = excel_mod.to_date(r[7])

            # --- Sichtbare Ausgabe ---
            print(f"\n[Excel Row {i}]")
            print(f"  name_raw   = {r[0]}")
            print(f"  surname    = {surname}")
            print(f"  name       = {name}")
            print(f"  address    = street='{street}', number='{number}', zip='{plz}', city='{city}'")
            print(f"  phone      = {r[2]}")
            print(f"  hobbies    = {hobbies}")
            print(f"  email      = {r[4]}")
            print(f"  gender     = {r[5]}  | interested_in = {r[6]}")
            print(f"  birthdate  = {bday}")
            # -------------------------

            # Assertions
            self.assertTrue((surname is None and name) or (surname and name))
            self.assertIsInstance((street, number, plz, city), tuple)
            self.assertIsInstance(hobbies, list)
            if bday is not None:
                self.assertIsInstance(bday, date)


# =============== XML: 3 Beispieldatensätze ===============
class TestXmlExamples(unittest.TestCase):
    def test_xml_three_users(self):
        xml_text = """<root>
          <user>
            <email>a@ex.com</email>
            <name>Doe, Alice</name>
            <hobby>Chess</hobby>
          </user>
          <user>
            <email>b@ex.com</email>
            <name>Müller, Bob</name>
            <hobby>Gaming</hobby>
            <hobby>Cooking</hobby>
          </user>
          <user>
            <email>c@ex.com</email>
            <name>Charlie</name>
          </user>
        </root>"""
        root = xml_mod.etree.fromstring(xml_text.encode("utf-8"))
        users = root.findall(".//user")
        self.assertEqual(len(users), 3)

        for i, u in enumerate(users, start=1):
            email = (u.findtext("email") or "").strip()
            name_raw = (u.findtext("name") or "").strip()
            s, n = excel_mod.split_name(name_raw)
            hobbies = [h.text for h in u.findall("hobby")]

            # --- Sichtbare Ausgabe ---
            print(f"\n[XML User {i}]")
            print(f"  email      = {email}")
            print(f"  name_raw   = {name_raw}")
            print(f"  surname    = {s}")
            print(f"  name       = {n}")
            print(f"  hobbies    = {hobbies}")
            # -------------------------

            # Assertions
            self.assertIn("@", email)
            self.assertTrue((s is None and n) or (s and n))
            self.assertIsInstance(hobbies, list)


# =============== Mongo: 3 Beispieldatensätze ===============
class TestMongoExamples(unittest.TestCase):
    def test_mongo_three_docs(self):
        docs = [
            {
                "_id": "u1@ex.com",
                "name": "Doe, Uwe",
                "phone": "111",
                "createdAt": "2024-03-01",
                "updatedAt": "2024-03-07",
                "friends": ["f1@ex.com"],
                "likes": [{"liked_email":"l@ex.com","timestamp":"2024-01-02","status":"ok"}],
                "messages": [{"receiver_email":"m@ex.com","conversation_id":"c1","message":"hi","timestamp":"2024-02-02"}],
            },
            {
                "_id": "u2@ex.com",
                "name": "Anna",
                "phone": "222",
                "createdAt": "2000-01-01",
                "updatedAt": "",
                "friends": [],
                "likes": [],
                "messages": [],
            },
            {
                "_id": "u3@ex.com",
                "name": "Müller, Carl",
                "phone": None,
                "createdAt": None,
                "updatedAt": None,
                "friends": ["x@ex.com","y@ex.com"],
                "likes": [],
                "messages": [],
            },
        ]
        for i, d in enumerate(docs, start=1):
            email = str(d.get("_id","")).lower()
            s, n = excel_mod.split_name(d.get("name", ""))
            created = mongo_mod.to_date(d.get("createdAt"))
            updated = mongo_mod.to_date(d.get("updatedAt"))
            friends = d.get("friends", [])
            likes = d.get("likes", [])
            messages = d.get("messages", [])

            # --- Sichtbare Ausgabe ---
            print(f"\n[Mongo Doc {i}]")
            print(f"  email      = {email}")
            print(f"  name_raw   = {d.get('name')}")
            print(f"  surname    = {s}")
            print(f"  name       = {n}")
            print(f"  createdAt  = {created}")
            print(f"  updatedAt  = {updated}")
            print(f"  friends    = {friends}")
            print(f"  likes      = {likes}")
            print(f"  messages   = {messages}")
            # -------------------------

            # Assertions
            self.assertIn("@", email)
            self.assertTrue(n is not None)
            if created is not None: self.assertIsInstance(created, date)
            if updated is not None: self.assertIsInstance(updated, date)
            self.assertIsInstance(friends, list)
            self.assertIsInstance(likes, list)
            self.assertIsInstance(messages, list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
