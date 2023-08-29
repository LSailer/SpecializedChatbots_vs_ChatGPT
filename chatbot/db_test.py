import unittest
import db


class TestDB(unittest.TestCase):
    def setUp(self):
        self.connection = db.create_connection()
        self.session = "UnitTest"

    def tearDown(self):
        # self.cursor.close()

        self.connection.close()

    def test_create_connection(self):
        connection = db.create_connection()
        self.assertIsNotNone(connection)

    def test_check_create_database(self):
        db.check_create_database()
        tables = (
            "Question",
            "Response",
            "FAQ",
            "Classification")
        result = self.connection.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' and name in {0} ".format(tables))
        count = result.fetchone()[0]
        self.assertEqual(count, len(tables))

    def test_save_question_answer_classification(self):
        db.save_question_answer_classification('Anlage', ['Wie kann ich die Dok... verwenden', 'Wie kann ich neue Re... erstellen'], [
                                               'anlegung_document', 'anlegung_register'], [0.43075627, 0.30570045], self.session)


if __name__ == '__main__':
    unittest.main()
