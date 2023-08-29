import inspect
import os
import numpy as np
from nltk.corpus import stopwords
import nltk
from nltk.stem.snowball import GermanStemmer

stemmer = GermanStemmer()


def get_path(file, frame=None):
    if frame is None:
        frame = inspect.currentframe()
    path = os.path.dirname(os.path.abspath(inspect.getfile(frame))) # type: ignore
    path = os.path.join(path, file).replace("\\", "/")
    return path


def get_json_path():
    path = os.path.dirname(os.path.abspath(
        inspect.getfile(get_json_path)))
    path = os.path.join(path, 'chat.json').replace("\\", "/")
    return path


def frage_bearbeitung(frage):
    sentence_word = nltk.word_tokenize(frage)
    stop = stopwords.words('german')
    ignore_words = ['?', '.', ','] + stop
    sentence_words = []
    for word in sentence_word:
        if word not in ignore_words or word == 'weiter' or word == 'andere' or word == 'nicht':
            sentence_words.append(word)
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words


def bow(frage, words, show_details=False):
    sentence_words = frage_bearbeitung(frage)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)
