import math


class Songs:
    first_list = []
    second_list = []
    third_list = []
    fourth_list = []  # list of objects / songs in each quadrant

    def __init__(self, title, artist, coord):
        self.title = title
        self.artist = artist
        self.coord = coord

    def getCoord(self):
        return self.coord

    def getQuadrantList(self):  # list of songs in that quadrant
        x = self.getCoord()[0]
        y = self.getCoord()[1]

        if x > 0 and y > 0:  # 1st
            quad_list = Songs.first_list
            return quad_list

        elif x < 0 and y > 0:  # 2nd
            quad_list = Songs.second_list
            return quad_list

        elif x < 0 and y < 0:  # 3rd
            quad_list = Songs.third_list
            return quad_list

        elif x > 0 and y < 0:  # 4th
            quad_list = Songs.fourth_list
            return quad_list

        else:
            return None

    def getDelta(self, target):  # finds the difference in x and y between two points
        x = self.getCoord()[0]
        y = self.getCoord()[1]

        target_x = target.getCoord()[0]
        target_y = target.getCoord()[1]

        delta_x = target_x - x
        delta_y = target_y - y

        return delta_x, delta_y

    def calc(self, target, minimum_songs=None):  # the angle algorithm
        if minimum_songs is None:
            minimum_songs = [self]

        delta_x, delta_y = self.getDelta(target)
        current_list = self.getQuadrantList()

        target_angle = math.degrees(math.atan2(delta_y, delta_x)) % 360

        lower_bound = (target_angle - 20) % 360
        upper_bound = (target_angle + 20) % 360  # angle ranges

        filtered_list = []

        for song in current_list:  # removing angles outside the range
            if song in minimum_songs:
                continue

            delta_x, delta_y = self.getDelta(song)

            angle = math.degrees(math.atan2(delta_y, delta_x)) % 360

            # handle wrap-around
            if lower_bound < upper_bound:
                if lower_bound <= angle <= upper_bound:
                    filtered_list.append(song)
            else:  # wrap-around case
                if angle >= lower_bound or angle <= upper_bound:
                    filtered_list.append(song)

        if not filtered_list:  # if the list is empty - meaning no more songs in the same quadrant within the range
            return minimum_songs  # returns the list made for the quadrant it's in

        minimum_song = None
        minimum_distance = float('inf')

        # finds the minimum Euclidean distance
        minimum_song = min(
            filtered_list,
            key=lambda s: math.hypot(*(self.getDelta(s))),
            default=None
        )

        if minimum_song is None:
            return minimum_songs

        if minimum_song != target:  # if it isn't target recursively call function with the next node
            minimum_songs.append(minimum_song)
            return minimum_song.calc(target, minimum_songs)
        else:
            minimum_songs.append(minimum_song)
            return minimum_songs

    def transition(self, target):  # when an axis is met and need to transition to another quadrant
        x = self.getCoord()[0]
        y = self.getCoord()[1]

        transition_list = (
                Songs.first_list + Songs.second_list + Songs.third_list + Songs.fourth_list
        )
        transition_list = [s for s in transition_list if s != self]

        delta_x, delta_y = self.getDelta(target)

        target_angle = math.degrees(math.atan2(delta_y, delta_x)) % 360

        lower_bound = (target_angle - 20) % 360
        upper_bound = (target_angle + 20) % 360  # angle ranges

        filtered_transition_list = []

        for song in transition_list:  # removing angles outside the range

            delta_x, delta_y = self.getDelta(song)

            angle = math.degrees(math.atan2(delta_y, delta_x)) % 360

            if lower_bound < upper_bound:
                if lower_bound <= angle <= upper_bound:
                    filtered_transition_list.append(song)
            else:  # wrap-around
                if angle >= lower_bound or angle <= upper_bound:
                    filtered_transition_list.append(song)

        if not filtered_transition_list:
            return None

        # closest song
        minimum_song = min(
            filtered_transition_list,
            key=lambda s: math.hypot(*self.getDelta(s)),
            default=None
        )
        return minimum_song

    def find_playlist(self, target, playlist=None):

        if playlist is None:  # will only be None at the start
            playlist = self.calc(target)
        else:
            playlist += [s for s in self.calc(target) if s not in playlist]

        if target in playlist:  # if target is in the same quadrant as the starting point
                                # then no need for transition
            return playlist

        current_song = playlist[-1]  # last song in the current playlist
        next_song = current_song.transition(target)  # next song after transitioning to another quadrant

        if next_song == target:
            playlist.append(target)
            return playlist

        return next_song.find_playlist(target, playlist)  # if next_song is not target repeat
                                                          # the same for the new quadrant


    @classmethod
    def get_named_playlist(cls, objects_list):  # returns the song names in the playlist
        playlist = []

        index = 0

        while index < len(objects_list):  # remove the starting and target objects
            if objects_list[index].artist is None:
                objects_list.pop(index)
            else:
                index += 1

        for objects in objects_list:
            playlist.append(objects.title + ' - ' + objects.artist)

        return playlist


    @classmethod
    def delete_object(cls, obj):
        x, y = obj.getCoord()

        if x > 0 and y > 0 and obj in Songs.first_list: Songs.first_list.remove(obj)
        elif x < 0 and y > 0 and obj in Songs.second_list: Songs.second_list.remove(obj)
        elif x < 0 and y < 0 and obj in Songs.third_list: Songs.third_list.remove(obj)
        elif x > 0 and y < 0 and obj in Songs.fourth_list: Songs.fourth_list.remove(obj)


class FirstQuadrant(Songs):

    def __init__(self, title, artist, coord):
        super().__init__(title, artist, coord)
        Songs.first_list.append(self)



class SecondQuadrant(Songs):

    def __init__(self, title, artist, coord):
        super().__init__(title, artist, coord)
        Songs.second_list.append(self)



class ThirdQuadrant(Songs):

    def __init__(self, title, artist, coord):
        super().__init__(title, artist, coord)
        Songs.third_list.append(self)



class FourthQuadrant(Songs):

    def __init__(self, title, artist, coord):
        super().__init__(title, artist, coord)
        Songs.fourth_list.append(self)



def get_quadrant_object(title, coord):  # for the starting and target objects
    if coord[0] > 0 and coord[1] > 0:
        return FirstQuadrant(title, None, coord)
    elif coord[0] < 0 < coord[1]:
        return SecondQuadrant(title, None, coord)
    elif coord[0] < 0 and coord[1] < 0:
        return ThirdQuadrant(title, None, coord)
    else:
        return FourthQuadrant(title, None, coord)
