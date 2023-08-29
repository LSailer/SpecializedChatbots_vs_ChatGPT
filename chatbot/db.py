from datetime import datetime
import psycopg2
import os
import subprocess
import sqlite3


# Verbindung zur PostgreSQL-Datenbank herstellen


def create_connection():
    try:
        local_database_path = "faq.db"
        # Generate a local PostgreSQL file using pg_dump
        connection = sqlite3.connect(local_database_path)
        return connection
    except sqlite3.Error as error:
        print("Fehler beim Generieren der lokalen PostgreSQL-Datenbankdatei:", error)
        return None


# Überprüfen, ob die Datenbank existiert, andernfalls erstellen


def check_create_database():
    try:
        with create_connection() as connection:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS Question (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Request TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Response (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Answer TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Classification (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT
            );
            CREATE TABLE IF NOT EXISTS FAQ (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                QuestionID INTEGER,
                ResponseID INTEGER,
                Classification_ID INTEGER,
                Probability REAL,
                Date TEXT NOT NULL,
                Session TEXT NOT NULL,
                Feedback TEXT,
                FOREIGN KEY (QuestionID) REFERENCES Question(ID),
                FOREIGN KEY (ResponseID) REFERENCES Response(ID),
                FOREIGN KEY (Classification_ID) REFERENCES Classification(ID)
            );
        """
            connection.executescript(create_table_query)
    except sqlite3.Error as error:
        print("Fehler beim Überprüfen/Erstellen der Datenbank:", error)


# Funktion zum Speichern der Frage, Antwort, Klassifizierung und Wahrscheinlichkeit in der Datenbank


def save_question_answer_classification(
    question, answers, classifications, probabilities, session
):
    try:
        connection = create_connection()
        check_create_database()
        if connection is None:
            return

        cursor = connection
        ids = []
        for i in range(len(classifications)):
            insert_id = insert_question_answer_classification(
                question,
                str(answers),
                classifications[i],
                probabilities[i],
                session,
                connection,
            )
            ids.append(insert_id)
        connection.commit()
        cursor.close()
        connection.close()
        return ids
    except sqlite3.Error as error:
        print("Fehler beim Speichern der Frage und Antwort in der Datenbank:", error)


def insert_question_answer_classification(
    question, answer, classification, probability, session, connection
):
    question_id = get_or_insert_id("Question", "Request", question, connection)
    answer_id = get_or_insert_id("Response", "Answer", answer, connection)
    classification_id = get_or_insert_id(
        "Classification", "Name", classification, connection
    )
    insert_query = "INSERT INTO FAQ (QuestionID, ResponseID, Classification_ID, Probability, Date, Session) VALUES (?, ?, ?, ?, ?, ?) RETURNING rowid"
    result = connection.execute(
        insert_query,
        (
            question_id,
            answer_id,
            classification_id,
            str(probability),
            datetime.now(),
            session,
        ),
    ).fetchone()[0]
    return result


def get_or_insert_id(table, column, value, connection):
    response = connection.execute(
        f"SELECT rowid FROM {table} WHERE {column} = ?", (value,)
    ).fetchone()
    if response is None:
        insert_query = f"INSERT INTO {table} ({column}) VALUES (?) RETURNING rowid"
        result = connection.execute(insert_query, (value,)).fetchone()[0]
    else:
        result = response[0]
    return result


def give_feedback(ids, feedback):
    try:
        connection = create_connection()
        if connection is None:
            return
        cursor = connection.cursor()
        for id in ids:
            update_query = "UPDATE FAQ SET Feedback = ? WHERE rowid = ?"
            cursor.execute(update_query, (feedback, id))
        connection.commit()
        cursor.close()
        connection.close()
    except sqlite3.Error as error:
        print("Fehler beim Speichern des Feedbacks in der Datenbank:", error)
