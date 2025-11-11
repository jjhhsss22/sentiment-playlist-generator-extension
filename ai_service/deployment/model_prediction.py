import numpy as np
from .preprocessing import preprocess
from tensorflow.errors import InvalidArgumentError
import tensorflow as tf


# def load():
#     sentiment_model = tf.keras.models.load_model("model/sentiment_model3.keras", compile=False)
#
#     sentiment_model.compile(optimizer='adam',
#                             loss='categorical_crossentropy',
#                             metrics=['accuracy'])
#
#     return sentiment_model


EMOTIONS = [
    'Anger', 'Boredom', 'Empty', 'Enthusiasm', 'Fun', 'Happiness',
    'Hate', 'Love', 'Neutral', 'Relief', 'Sadness', 'Surprise', 'Worry'
]

EMOTION_COORDS = [
    (-10, 9), (-3, -8), (-5, -4), (6, 7), (8, 8), (10, 9),
    (-8, 7), (9, 5), (0, 0), (8, -8), (-10, -9), (2, 8), (-1, -7)
]


# ml model sentiment prediction
def predict(model, input_text: str):
    final_token = preprocess(input_text)
    try:
        predictions = model.predict(final_token)
        return predictions
    except InvalidArgumentError:
        raise ValueError("Unable to predict sentiment")

# return the name of the most likely emotion
def get_predicted_emotion(predictions) -> str:
    index = np.argmax(predictions)
    return EMOTIONS[index]

# weighted average coordinate algorithm based on emotion probabilities
def get_starting_coord(predictions) -> tuple:
    final_coord = (0, 0)
    for i, emotion in enumerate(EMOTIONS):
        factor = round(predictions[i], 5)
        weighted_tuple = tuple(e * factor for e in EMOTION_COORDS[i])
        final_coord = tuple(round(a + b, 5) for a, b in zip(final_coord, weighted_tuple))
    return final_coord

# return coordinate of the desired target emotion
def get_target_coord(target_emotion: str) -> tuple:
    index = EMOTIONS.index(target_emotion)
    return EMOTION_COORDS[index]