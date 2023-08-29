from flask import Flask, render_template, request, session
import nltk
from nltk.stem.snowball import GermanStemmer

stemmer = GermanStemmer()
from nltk.corpus import stopwords
import numpy as np

import tflearn
import random
import os
import inspect
import pickle
import json
from db import save_question_answer_classification, give_feedback
from waitress import serve
import uuid


def get_path(file, frame=None):
    if frame is None:
        frame = inspect.currentframe()
    path = os.path.dirname(os.path.abspath(inspect.getfile(frame)))  # type: ignore
    path = os.path.join(path, file).replace("\\", "/")
    return path


def get_json_path():
    path = os.path.dirname(os.path.abspath(inspect.getfile(get_json_path)))
    path = os.path.join(path, "chat.json").replace("\\", "/")
    return path


# importiere die Dialogdesign-Datei
with open(get_json_path(), mode="r", encoding="utf8") as json_data:
    dialogflow = json.load(json_data)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "ENAIO-Chatbot"

# wiederherstelle alle unsere Datenstrukturen
data = pickle.load(open("model\\train_data", "rb"))
words = data["words"]
classes = data["classes"]
train_x = data["train_x"]
train_y = data["train_y"]


@app.route("/")
def home():
    session["user_id"] = str(uuid.uuid4())
    return render_template("chat.html")


@app.route("/get", methods=["POST"])
def chatbot_response():
    msg = request.form["msg"]
    res = antwort(msg)
    return res


@app.route("/giveFeedBack", methods=["POST"])
def chatbot_give_feedback():
    # Get data from the POST request
    # Extract the necessary values
    feedback = request.form["feedback"]
    db_id = request.form["db_id"]
    db_id = db_id.split(",")
    if feedback is None or db_id is None:
        return "Missing data", 400
    # Get the feedback from the database
    give_feedback(db_id, feedback)
    return "Feedback gespeichert"


# Aufbau unseres Antwortprozessors.
# Erstellen einer Datenstruktur, die den Benutzerkontext enthält
context = {}

import tflearn

# Aufbau des neuronalen Netzes
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 64)
net = tflearn.fully_connected(net, 64)
net = tflearn.fully_connected(net, len(train_y[0]), activation="softmax")
net = tflearn.regression(net)


# Definiere das Modell und konfiguriere tensorboard
model = tflearn.DNN(net)

# Define your synonyms
synonyms = {"ordner": "akte", "dateien": "dokument", "vorgang": "register"}


# Bearbeitung der Benutzereingaben, um einen bag-of-words zu erzeugen
def frageBearbeitung(frage):
    # tokenisiere die synonymen
    sentence_word = nltk.word_tokenize(frage, language="german")
    # generiere die Stopwörter
    stop = stopwords.words("german")
    ignore_words = ["?", ".", ","] + stop
    ######Korrektur Schreibfehler
    ignore_words = set([stemmer.stem(word.lower()) for word in ignore_words])
    sentence_words = [
        stemmer.stem(synonyms.get(word.lower(), word).lower()) for word in sentence_word
    ]
    ret_list = []
    for word in sentence_words:
        if (
            word not in ignore_words
            or word == "weiter"
            or word == "andere"
            or word == "nicht"
        ):
            # a=correction(word)
            ret_list.append(word)
    # stemme jedes Wort
    return ret_list


def compute_bow(words_list, reference_list):
    return [1 if word in words_list else 0 for word in reference_list]


def word_in_reference_list(words_list, reference_list):
    return [1 if word in reference_list else 0 for word in words_list]


# Rückgabe bag of words array: 0 oder 1 für jedes Wort in der 'bag', die im Satz existiert
def bow(frage, words, show_details=False):
    sentence_words = frageBearbeitung(frage)
    if show_details:
        print(word_in_reference_list(sentence_words, words))
    return np.array(compute_bow(sentence_words, words))


# lade unsre gespeicherte Modell
model.load("model\\model.tflearn")

# Aufbau unseres Antwortprozessors.
# Erstellen einer Datenstruktur, die den Benutzerkontext enthält
context = {}


def klassifizieren(frage):
    ERROR_THRESHOLD = 0.35
    # generiere Wahrscheinlichkeiten von dem Modell
    results = model.predict([bow(frage, words)])[0]
    # herausfiltern Vorhersagen unterhalb eines Schwellenwerts
    results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]
    # nach Stärke der Wahrscheinlichkeit sortieren
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = {}
    for r in results:
        return_list[classes[r[0]]] = r[1]
    return return_list


def antwort(frage):
    BIAS_CORRECTION = 0.4
    results = klassifizieren(frage)
    print(results)
    try:
        # Wenn wir eine Klassifizierung haben, dann suchen wir das passende dialog-intent
        if not results:
            response =  ["Entschuldigung, ich konnte keine passende Absicht zu Ihrer aktuellen Frage identifizieren. Es scheint, als habe ich Ihre Frage nicht richtig verstanden. Könnten Sie bitte Ihre Anfrage anders formulieren oder weitere Details hinzufügen? Vielen Dank für Ihr Verständnis."]
        else:
            max_prob = max(results.values())

            searchintents = [
                i
                for i in dialogflow["dialogflow"]
                if i["intent"] in results
                and results[i["intent"]] >= max_prob - BIAS_CORRECTION
            ]
            if len(searchintents) > 1:
                response = [random.choice(i["synonym"]) for i in searchintents]
            else:
                response = [random.choice(searchintents[0]["antwort"])]

        db_id = save_question_answer_classification(
            frage,
            response,
            list(results.keys()),
            list(results.values()),
            session["user_id"],
        )
        return {"res": response, "db_ids": db_id}
    except (StopIteration, IndexError):
        # Wenn wir keine Klassifizierung haben, dann geben wir eine Standardantwort zurück
        return "Beim Chatbot ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut."


if __name__ == "__main__":
    # app.run(debug=True)
    # serve(app, host="0.0.0.0", port=12897)
    app.run(host="0.0.0.0", port=12897, debug=False)
