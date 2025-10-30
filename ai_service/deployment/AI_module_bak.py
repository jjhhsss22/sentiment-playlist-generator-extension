import tensorflow as tf
import neattext.functions as nt
import joblib
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import numpy as np


# sentiment analysis model
sentiment_model = tf.keras.models.load_model("../model/sentiment_model3.keras", compile=False)

sentiment_model.compile(optimizer='adam',
                        loss='categorical_crossentropy',
                        metrics=['accuracy'])


# stopwords
def remove_stopwords(input_text):
    return nt.remove_stopwords(input_text)


# stemming
def stem(sw_removed_text):
    ps = PorterStemmer()

    words = word_tokenize(sw_removed_text)
    stemmed_words = [ps.stem(word) for word in words]

    return ' '.join(stemmed_words)


# vectorisation
def vectorise(stemmed_text):
    count_vectorizer = joblib.load("../cv/count_vectorizer3.joblib")

    processed_text = count_vectorizer.transform([stemmed_text])
    return processed_text

# preprocess
def preprocess(input_text):  # combination of all three preprocessing functions
    final_text = vectorise(stem(remove_stopwords(str(input_text))))
    return final_text


# emotion prediction
def predict(input_text):
    final_text = preprocess(input_text)
    predictions = sentiment_model.predict(final_text)

    return predictions


# convert Python array to a list
def to_list(array):
    result_list = array.tolist()

    return result_list


emotion_coordinates = [(-10, 9), (-3, -8), (-5, -4),
                       (6, 7), (8, 8), (10, 9),
                       (-8, 7), (9, 5), (0, 0),
                       (8, -8), (-10, -9), (2, 8), (-1, -7)]


# find the most likely emotion
def get_predicted_emotion(predictions):
    emotion = ['Anger', 'Boredom', 'Empty',
           'Enthusiasm', 'Fun', 'Happiness',
           'Hate', 'Love', 'Neutral',
           'Relief', 'Sadness', 'Surprise', 'Worry']

    predicted_index = np.argmax(predictions)
    predicted_emotion = emotion[predicted_index]

    return predicted_emotion


# Algorithm to find the initial coord on the VA graph
def get_starting_coord(predictions):
    emotion = ['Anger', 'Boredom', 'Empty',
               'Enthusiasm', 'Fun', 'Happiness',
               'Hate', 'Love', 'Neutral',
               'Relief', 'Sadness', 'Surprise', 'Worry']

    final_coordinate = (0, 0)

    for i in range(len(emotion)):
        factor = round(predictions[0][i], 5)
        multiplied_tuple = tuple(element * factor for element in emotion_coordinates[i])

        final_coordinate = tuple(round(x + y, 5) for x, y in zip(final_coordinate, multiplied_tuple))

    return final_coordinate


# function to get the desired emotion
def get_target_coord(wanted_emotion):
    emotion = ['Anger', 'Boredom', 'Empty',
               'Enthusiasm', 'Fun', 'Happiness',
               'Hate', 'Love', 'Neutral',
               'Relief', 'Sadness', 'Surprise', 'Worry']

    target_coord = None

    for emotions in emotion:
        if emotions == wanted_emotion:
            index = emotion.index(emotions)
            target_coord = emotion_coordinates[index]

    return target_coord
