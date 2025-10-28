from flask import jsonify, request, Blueprint, current_app, render_template
from flask_login import login_required, current_user
from database.dbmodels import Playlist

api_profile_bp = Blueprint('api_profile', __name__)

@api_profile_bp.route('/profile', methods=['GET'])
@login_required
def api_profile():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return render_template("unknown.html"), 403

    try:
        playlists = Playlist.query.filter_by(user_id=current_user.id).all()  # query the database for all playlists
                                                                             # created by the current user and store it in a list
        playlist_data =[]

        for playlist in playlists:
            playlist_data.append({
                "prompt": playlist.prompt,
                "start_emotion": playlist.start_emotion,
                "target_emotion": playlist.target_emotion,
                "playlist": playlist.playlist.split(','),  # convert the comma-separated string to a list
                "creation_date": playlist.playlist_creation_date
            })  # for each playlist, create a different list with all its information in a dictionary

        playlist_data.reverse()  # reverse the list so that the most recent playlists are at the top of the page

        return jsonify(playlist_data)

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({"success": "false", "message": "Database error" })