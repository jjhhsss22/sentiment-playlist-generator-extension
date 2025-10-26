from flask import request, jsonify, Blueprint, current_app, render_template
from flask_login import login_required, current_user

from tensorflow.errors import InvalidArgumentError

from dbmodels import db, Playlist
from AIModel import predict, get_predicted_emotion, get_starting_coord, get_target_coord, to_list
from Music import Songs, get_quadrant_object


api_home_bp = Blueprint('api_home', __name__)

@api_home_bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return render_template("unknown.html"), 403

    data = request.get_json()

    input_text = data.get("text", "").strip()
    desired_emotion = data.get("emotion", None)

    emotions = ['Anger', 'Boredom', 'Empty',
                'Enthusiasm', 'Fun', 'Happiness',
                'Hate', 'Love', 'Neutral',
                'Relief', 'Sadness', 'Surprise', 'Worry']

    if not input_text or not desired_emotion:
        return jsonify({
            "success": False,
            "message": "Please fill out all forms for a playlist to be generated"
        })

    try:
        try:
            predictions = predict(input_text)  # 2D array with probabilities of emotions
        except InvalidArgumentError:
            return jsonify({
                "success": False,
                "message": "Please submit text in full sentences"
            })

        predicted_emotion = get_predicted_emotion(predictions)  # most likely emotion

        starting_coord = get_starting_coord(predictions)  # starting coord algorithm applied
        target_coord = get_target_coord(desired_emotion)  # target coord found using the checkbox input

        start_object = get_quadrant_object("start", starting_coord)
        target_object = get_quadrant_object("target", target_coord)

        playlist = start_object.find_playlist(target_object)

        if len(playlist) <= 2:
            return jsonify({
                "success": False,
                "message": "No available songs with the provided emotions. You are already at your desired emotion!"
            })

        predictions_list = to_list(predictions[0])  # convert the 2D array to a list
        i = 0
        total_prediction_sum = 0

        while i < len(predictions_list):
            if predictions_list[i] < 0.05:  # filter out insignificant emotions
                del predictions_list[i]

                del emotions[i]
            else:
                total_prediction_sum += predictions_list[i]  # also find the total of the significant emotions
                i += 1  # for the OTHERS bar in home.html

        predictions_list_rounded = [round(p, 1) for p in predictions_list]
        others_prediction = round(1 - total_prediction_sum, 1)

        print(predictions_list_rounded)
        print(others_prediction)

        Songs.delete_object(start_object)
        Songs.delete_object(target_object)  # delete the temporary objects

        songs_playlist = Songs.get_named_playlist(playlist)  # convert the object list to named list
        songs_playlist_text = ', '.join(songs_playlist)  # convert the list into string

        new_playlist = Playlist(prompt=input_text,
                                start_emotion=predicted_emotion,
                                target_emotion=desired_emotion,
                                playlist=songs_playlist_text,
                                user_id=current_user.id)

        db.session.add(new_playlist)
        db.session.commit()  # add to the database

        return jsonify({
            "success": True,
            "message": "Playlist generated successfully!",
            "input_text": input_text,
            "desired_emotion": desired_emotion,
            "songs_playlist": songs_playlist,
            "predicted_emotions": emotions,
            "predictions_list": predictions_list_rounded,
            "others_prediction": others_prediction
        })  # pass our variables to the React frontend as JSON

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "message": "Error when generating playlist. Please try again."
        })