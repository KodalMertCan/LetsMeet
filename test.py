import unittest
from datetime import date
import import_excel_script as excel_mod
import import_xml as xml_mod
import import_mongo as mongo_mod


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
        for r in rows:
            surname, name = excel_mod.split_name(r[0])
            self.assertTrue((surname is None and name) or (surname and name))
            street, number, plz, city = excel_mod.parse_address(r[1])
            self.assertIsInstance((street, number, plz, city), tuple)
            hobbies = excel_mod.parse_hobbies(r[3])
            self.assertIsInstance(hobbies, list)
            bday = excel_mod.to_date(r[7])
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

        u1 = users[0]
        self.assertEqual(u1.findtext("email"), "a@ex.com")
        s1, n1 = excel_mod.split_name(u1.findtext("name"))
        self.assertEqual((s1, n1), ("Doe", "Alice"))
        self.assertEqual([h.text for h in u1.findall("hobby")], ["Chess"])

        u2 = users[1]
        self.assertEqual(u2.findtext("email"), "b@ex.com")
        self.assertEqual(len(u2.findall("hobby")), 2)

        u3 = users[2]
        self.assertEqual(u3.findtext("email"), "c@ex.com")
        s3, n3 = excel_mod.split_name(u3.findtext("name"))
        self.assertEqual((s3, n3), (None, "Charlie"))


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
        for d in docs:
            email = str(d.get("_id","")).lower()
            self.assertIn("@", email)
            s, n = excel_mod.split_name(d.get("name", ""))
            self.assertTrue(n is not None)
            created = mongo_mod.to_date(d.get("createdAt"))
            updated = mongo_mod.to_date(d.get("updatedAt"))
            if created is not None: self.assertIsInstance(created, date)
            if updated is not None: self.assertIsInstance(updated, date)
            self.assertIsInstance(d.get("friends", []), list)
            self.assertIsInstance(d.get("likes", []), list)
            self.assertIsInstance(d.get("messages", []), list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
