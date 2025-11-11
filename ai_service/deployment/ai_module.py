from flask import Flask, request, jsonify

from .model_prediction import predict, get_predicted_emotion, get_starting_coord, get_target_coord, EMOTIONS
from .utils import to_list, round_list

'''
turned ai module "microservice-ready" in case I need to scale ml model and want to run development on a separate server
so that it can be improved and reused.

can also turn it asynchronous using another server
'''

# filter out insignificant emotions
def calc_others_probability(array: list):
    valid_emotions = []
    valid_predictions = []

    i = 0
    total_prediction_sum = 0

    while i < len(array):
        if array[i] >= 0.05:
            total_prediction_sum += array[i]
            valid_emotions.append(EMOTIONS[i])
            valid_predictions.append(array[i])

        i += 1

    return round(1 - total_prediction_sum, 1), valid_emotions, valid_predictions

# main pipeline for Flask's /api/home route
def run_prediction_pipeline(model, input_text: str, desired_emotion: str):

    predictions = predict(model, input_text)
    predictions = to_list(predictions[0])
    likely_emotion = get_predicted_emotion(predictions)
    starting_coord = get_starting_coord(predictions)
    target_coord = get_target_coord(desired_emotion)
    others_probability, valid_emotions, valid_predictions = calc_others_probability(predictions)
    rounded_predictions = round_list(valid_predictions)
    return {
        "predictions_list": rounded_predictions,
        "predicted_emotions": valid_emotions,
        "likely_emotion": likely_emotion,
        "starting_coord": starting_coord,
        "target_coord": target_coord,
        "others_probability": others_probability,
    }