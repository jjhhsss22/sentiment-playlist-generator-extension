from music.music_logic.music_class import Songs, get_quadrant_object

def generate_playlist_pipeline(start_coord, target_coord):
    start_object = get_quadrant_object("start", start_coord)
    target_object = get_quadrant_object("target", target_coord)  # temporary objects for start & target

    object_playlist = start_object.find_playlist(target_object)  # recursive-angle algorithm

    Songs.delete_object(start_object)
    Songs.delete_object(target_object)  # delete the temporary objects

    playlist_list = Songs.get_named_playlist(object_playlist)  # convert the object list to named list
    playlist_text = ', '.join(playlist_list)  # convert the list into string separated by commas

    return {
            "playlist_list": playlist_list,
            "playlist_text": playlist_text,
        }
