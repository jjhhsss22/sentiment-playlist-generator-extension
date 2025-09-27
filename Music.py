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

        target_angle = math.degrees(math.atan2(delta_y, delta_x))

        upper_bound = target_angle + 20
        lower_bound = target_angle - 20  # angle ranges

        filtered_list = []

        for song in current_list:  # removing angles outside the range
            delta_x, delta_y = self.getDelta(song)

            angle = math.degrees(math.atan2(delta_y, delta_x))

            if lower_bound <= angle <= upper_bound and song != self:  # check if it's within the range
                filtered_list.append(song)

        if not filtered_list:  # if the list is empty - meaning no more songs in the same quadrant within the range
            return minimum_songs  # returns the list made for the quadrant it's in

        minimum_song = None
        minimum_distance = float('inf')

        for song in filtered_list:  # finds the minimum Euclidean distance

            delta_x, delta_y = self.getDelta(song)

            magnitude = math.sqrt(delta_x ** 2 + delta_y ** 2)

            if magnitude < minimum_distance and magnitude != 0:
                minimum_distance = magnitude
                minimum_song = song

        if minimum_song is not None:  # if minimum_song exists
            if minimum_song is not target:
                minimum_songs.append(minimum_song)
                return minimum_song.calc(target, minimum_songs)  # if minimum_song is not the target call the method again
            else:

                minimum_songs.append(minimum_song)
                return minimum_songs
        else:
            return "No songs found within the range"  # error handling

    def transition(self, target):  # when an axis is met and need to transition to another quadrant
        x = self.getCoord()[0]
        y = self.getCoord()[1]

        if x > 0 and y > 0:
            transition_list = Songs.second_list + Songs.third_list + Songs.fourth_list

        elif x < 0 and y > 0:
            transition_list = Songs.first_list + Songs.third_list + Songs.fourth_list

        elif x < 0 and y < 0:
            transition_list = Songs.first_list + Songs.second_list + Songs.fourth_list

        else:
            transition_list = Songs.first_list + Songs.second_list + Songs.third_list  # list of objects in the other 3 quadrants

        delta_x, delta_y = self.getDelta(target)

        target_angle = math.degrees(math.atan2(delta_y, delta_x))

        upper_bound = target_angle + 20
        lower_bound = target_angle - 20  # angle ranges

        filtered_transition_list = []

        for song in transition_list:  # removing angles outside the range

            delta_x, delta_y = self.getDelta(song)

            angle = math.degrees(math.atan2(delta_y, delta_x))

            if lower_bound <= angle <= upper_bound:
                filtered_transition_list.append(song)

        minimum_song = None
        minimum_distance = float('inf')

        for song in filtered_transition_list:  # finds the minimum Euclidean distance
            delta_x, delta_y = self.getDelta(song)

            magnitude = math.sqrt(delta_x ** 2 + delta_y ** 2)

            if magnitude < minimum_distance and magnitude != 0:
                minimum_distance = magnitude
                minimum_song = song

        return minimum_song

    def find_playlist(self, target, playlist=None):

        if playlist is None:  # will only be None at the start
            playlist = self.calc(target)
        else:
            playlist += self.calc(target)

        if target in playlist:  # if target is in the same quadrant as the starting point
                                # then no need for transition
            return playlist

        current_song = playlist[-1]  # last song in the current playlist

        next_song = current_song.transition(target)  # next song after transitioning to another quadrant

        if next_song is target:
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
        x = obj.getCoord()[0]
        y = obj.getCoord()[1]

        if x > 0 and y > 0:
            if obj in Songs.first_list:
                Songs.first_list.remove(obj)

        elif x < 0 and y > 0:
            if obj in Songs.second_list:
                Songs.second_list.remove(obj)

        elif x < 0 and y < 0:
            if obj in Songs.third_list:
                Songs.third_list.remove(obj)

        elif x > 0 and y < 0:
            if obj in Songs.fourth_list:
                Songs.fourth_list.remove(obj)



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



# 25 each add songs

# First Quadrant (Positive Valence, Positive Arousal)
# Valence (X): 1 to 10
# Arousal (Y): 1 to 10

song1 = FirstQuadrant("Good Time", "Owl City ft. Carly Rae Jepsen", (10, 10))
song2 = FirstQuadrant("Electric Feel", "MGMT", (9, 8))
song3 = FirstQuadrant("Pompeii", "Bastille", (8, 7))
song4 = FirstQuadrant("Take A Walk", "Passion Pit", (6, 8))
song5 = FirstQuadrant("We Are Young", "fun. ft. Janelle Monáe", (5, 7))
song6 = FirstQuadrant("Feel Good Inc.", "Gorillaz", (3, 5))
song7 = FirstQuadrant("Sweet Disposition", "The Temper Trap", (5, 5))
song8 = FirstQuadrant("Safe and Sound", "Capital Cities", (3, 4))
song9 = FirstQuadrant("A-Punk", "Vampire Weekend", (2, 3))
song10 = FirstQuadrant("Lisztomania", "Phoenix", (1, 1))
song11 = FirstQuadrant("Don't You Worry Child", "Swedish House Mafia ft. John Martin", (10, 6))
song12 = FirstQuadrant("Wake Me Up", "Avicii", (9, 5))
song13 = FirstQuadrant("Live It Up", "Aerosmith", (8, 4))
song14 = FirstQuadrant("On Top of the World", "Imagine Dragons", (6, 2))
song15 = FirstQuadrant("Dog Days Are Over", "Florence + The Machine", (6, 4))
song16 = FirstQuadrant("Shut Up and Dance", "Walk The Moon", (5, 1))
song17 = FirstQuadrant("Happy", "Pharrell Williams", (4, 10))
song18 = FirstQuadrant("Walking On Sunshine", "Katrina and the Waves", (3, 9))
song19 = FirstQuadrant("All Star", "Smash Mouth", (3, 7))
song20 = FirstQuadrant("Can't Stop the Feeling", "Justin Timberlake", (1, 7))
song21 = FirstQuadrant("Best Day of My Life", "American Authors", (7, 4))
song22 = FirstQuadrant("Go!", "The Chemical Brothers", (7, 3))
song23 = FirstQuadrant("It's My Life", "Bon Jovi", (7, 4))
song24 = FirstQuadrant("Everything Now", "Arcade Fire", (5, 3))
song25 = FirstQuadrant("Dance Monkey", "Tones and I", (6, 10))

# Second Quadrant (Negative Valence, Positive Arousal)
# Valence (X): -10 to -1
# Arousal (Y): 1 to 10

song26 = SecondQuadrant("Runaway", "Kanye West", (-10, 10))
song27 = SecondQuadrant("The Pretender", "Foo Fighters", (-9, 7))
song28 = SecondQuadrant("Hurt", "Nine Inch Nails", (-8, 9))
song29 = SecondQuadrant("Fell In Love With A Girl", "The White Stripes", (-9, 4))
song30 = SecondQuadrant("No One Knows", "Queens of the Stone Age", (-6, 8))
song31 = SecondQuadrant("Mr. Brightside", "The Killers", (-5, 4))
song32 = SecondQuadrant("Bury a Friend", "Billie Eilish", (-4, 4))
song33 = SecondQuadrant("Knights of Cydonia", "Muse", (-3, 3))
song34 = SecondQuadrant("The Hand That Feeds", "Nine Inch Nails", (-2, 4))
song35 = SecondQuadrant("Reptilia", "The Strokes", (-1, 1))
song36 = SecondQuadrant("Heart-Shaped Box", "Nirvana", (-10, 4))
song37 = SecondQuadrant("Toxic", "Britney Spears", (-9, 3))
song38 = SecondQuadrant("Paranoid", "Black Sabbath", (-8, 2))
song39 = SecondQuadrant("Unfinished Sympathy", "Massive Attack", (-7, 1))
song40 = SecondQuadrant("Back to Black", "Amy Winehouse", (-6, 10))
song41 = SecondQuadrant("Last Resort", "Papa Roach", (-5, 9))
song42 = SecondQuadrant("Stressed Out", "Twenty One Pilots", (-4, 8))
song43 = SecondQuadrant("Take the Power Back", "Rage Against the Machine", (-3, 7))
song44 = SecondQuadrant("Knights of Cydonia", "Muse", (-2, 6))
song45 = SecondQuadrant("The Kill", "30 Seconds to Mars", (-1, 5))
song46 = SecondQuadrant("Stronger", "Kanye West", (-8, 4))
song47 = SecondQuadrant("Smells Like Teen Spirit", "Nirvana", (-7, 3))
song48 = SecondQuadrant("Helena", "My Chemical Romance", (-6, 2))
song49 = SecondQuadrant("Sugar, We're Goin Down", "Fall Out Boy", (-5, 1))
song50 = SecondQuadrant("Sugar", "System of a Down", (-4, 10))

# Third Quadrant (Negative Valence, Negative Arousal)
# Valence (X): -10 to -1
# Arousal (Y): -10 to -1

song51 = ThirdQuadrant("The Night We Met", "Lord Huron", (-10, -10))
song52 = ThirdQuadrant("Self Control", "Frank Ocean", (-9, -9))
song53 = ThirdQuadrant("The Sound of Silence", "Simon & Garfunkel", (-8, -6))
song54 = ThirdQuadrant("No One Noticed", "The Marías", (-7, -9))
song55 = ThirdQuadrant("Creep", "Radiohead", (-6, -7))
song56 = ThirdQuadrant("Sailor Song", "Gigi Perez", (-6, -5))
song57 = ThirdQuadrant("Breathe Me", "Sia", (-2, -4))
song58 = ThirdQuadrant("All I Want", "Kodaline", (-3, -3))
song59 = ThirdQuadrant("Tears Dry on Their Own", "Amy Winehouse", (-1, -2))
song60 = ThirdQuadrant("Somewhere Over The Rainbow", "Israel Kamakawiwo'ole", (-1, -1))
song61 = ThirdQuadrant("Mad World", "Gary Jules", (-9, -5))
song62 = ThirdQuadrant("Ain't No Sunshine", "Bill Withers", (-9, -4))
song63 = ThirdQuadrant("Under the Bridge", "Red Hot Chili Peppers", (-7, -3))
song64 = ThirdQuadrant("About You", "The 1975", (-7, -2))
song65 = ThirdQuadrant("Say Something", "A Great Big World", (-6, -1))
song66 = ThirdQuadrant("Yesterday", "The Beatles", (-5, -10))
song67 = ThirdQuadrant("When We Were Young", "Adele", (-4, -9))
song68 = ThirdQuadrant("Let Her Go", "Passenger", (-3, -8))
song69 = ThirdQuadrant("Someone Like You", "Adele", (-2, -7))
song70 = ThirdQuadrant("The River", "Bruce Springsteen", (-1, -6))
song71 = ThirdQuadrant("Skinny Love", "Bon Iver", (-8, -6))
song72 = ThirdQuadrant("Sparks", "Coldplay", (-7, -4))
song73 = ThirdQuadrant("My Love Mine All Mine", "Mitski", (-6, -2))
song74 = ThirdQuadrant("The Scientist", "Coldplay", (-5, -1))
song75 = ThirdQuadrant("The Night We Met", "Lord Huron", (-4, -5))

# Fourth Quadrant (Positive Valence, Negative Arousal)
# Valence (X): 1 to 10
# Arousal (Y): -10 to -1

song76 = FourthQuadrant("The Lazy Song", "Bruno Mars", (10, -10))
song77 = FourthQuadrant("Banana Pancakes", "Jack Johnson", (9, -9))
song78 = FourthQuadrant("Breathe", "Pink Floyd", (8, -5))
song79 = FourthQuadrant("Wonderful Tonight", "Eric Clapton", (7, -9))
song80 = FourthQuadrant("Landslide", "Fleetwood Mac", (6, -6))
song81 = FourthQuadrant("Harvest Moon", "Neil Young", (5, -2))
song82 = FourthQuadrant("The Weight", "The Band", (3, -4))
song83 = FourthQuadrant("Stay", "Rihanna ft. Mikky Ekko", (3, -3))
song84 = FourthQuadrant("Gravity", "John Mayer", (2, -2))
song85 = FourthQuadrant("I Will Follow You Into the Dark", "Death Cab for Cutie", (1, -1))
song86 = FourthQuadrant("Let It Be", "The Beatles", (10, -4))
song87 = FourthQuadrant("Come Away With Me", "Norah Jones", (9, -3))
song88 = FourthQuadrant("Jolene", "Dolly Parton", (8, -2))
song89 = FourthQuadrant("Fields of Gold", "Sting", (7, -1))
song90 = FourthQuadrant("Wonderwall", "Oasis", (6, -5))
song91 = FourthQuadrant("Your Best American Girl", "Mitski", (5, -7))
song92 = FourthQuadrant("Hallelujah", "Jeff Buckley", (4, -7))
song93 = FourthQuadrant("The One That Got Away", "Katy Perry", (3, -8))
song94 = FourthQuadrant("Fix You", "Coldplay", (2, -9))
song95 = FourthQuadrant("Hurt", "Christina Aguilera", (1, -10))
song96 = FourthQuadrant("I Won't Give Up", "Jason Mraz", (3, -8))
song97 = FourthQuadrant("Summertime", "DJ Jazzy Jeff & The Fresh Prince", (2, -1))
song98 = FourthQuadrant("Yellow", "Coldplay", (1, -3))
song99 = FourthQuadrant("At Last", "Etta James", (6, -2))
song100 = FourthQuadrant("Moon River", "Andy Williams", (7, -3))



# song1 = FirstQuadrant("Happy", "Pharrell Williams", (8, 9))
# song2 = FirstQuadrant("Uptown Funk", "Mark Ronson ft. Bruno Mars", (5, 7))
# song3 = FirstQuadrant("Shake It Off", "Taylor Swift", (3, 4))
# song4 = FirstQuadrant("Can't Stop the Feeling", "Justin Timberlake", (6, 8))
# song5 = FirstQuadrant("Walking on Sunshine", "Katrina and the Waves", (9, 6))
# song6 = FirstQuadrant("Shut Up and Dance", "WALK THE MOON", (7, 5))
# song7 = FirstQuadrant("Blinding Lights", "The Weeknd", (4, 6))
# song8 = FirstQuadrant("Roar", "Katy Perry", (6, 7))
# song9 = FirstQuadrant("Firework", "Katy Perry", (5, 4))
# song10 = FirstQuadrant("Stronger", "Kanye West", (9, 9))
# song11 = FirstQuadrant("Don't Stop Me Now", "Queen", (10, 10))
# song12 = FirstQuadrant("Sugar", "Maroon 5", (4, 3))
# song13 = FirstQuadrant("Levitating", "Dua Lipa", (7, 8))
# song14 = FirstQuadrant("24K Magic", "Bruno Mars", (5, 5))
# song15 = FirstQuadrant("Dance Monkey", "Tones and I", (9, 4))
# song16 = FirstQuadrant("We Found Love", "Rihanna ft. Calvin Harris", (6, 3))
# song17 = FirstQuadrant("Higher Love", "Kygo & Whitney Houston", (8, 7))
# song18 = FirstQuadrant("Good as Hell", "Lizzo", (3, 8))
# song19 = FirstQuadrant("Treasure", "Bruno Mars", (5, 6))
# song20 = FirstQuadrant("Wake Me Up", "Avicii", (7, 10))
# song21 = FirstQuadrant("Summer", "Calvin Harris", (4, 5))
# song22 = FirstQuadrant("On Top of the World", "Imagine Dragons", (6, 4))
# song23 = FirstQuadrant("Pompeii", "Bastille", (3, 3))
# song24 = FirstQuadrant("Shivers", "Ed Sheeran", (5, 9))
# song25 = FirstQuadrant("Call Me Maybe", "Carly Rae Jepsen", (2, 6))



# a = FirstQuadrant("a", "a", (1, 2))
# a2 = FirstQuadrant("a2", "a", (3, 2))
# a3 = FirstQuadrant("a3", "a", (10, 10))
# a4 = FirstQuadrant("a4", "a", (9, 9))
# a5 = FirstQuadrant("a5", "a", (7, 1))
# a6 = FirstQuadrant("a6", "a", (1, 9))
# a7 = FirstQuadrant("a7", "a", (2, 7))
# a8 = FirstQuadrant("a8", "a", (10, 2))
# a9 = FirstQuadrant("a9", "a", (9, 5))
# a10 = FirstQuadrant("a10", "a", (3, 9))
# a11 = FirstQuadrant("a11", "a", (8, 8))
# a12 = FirstQuadrant("a12", "a", (8.5, 8.8))
#
# b = SecondQuadrant("b", "a", (-1, 2))
# b2 = SecondQuadrant("b2", "a", (-6, 3))
# b3 = SecondQuadrant("b3", "a", (-4, 1))
# b4 = SecondQuadrant("b4", "a", (-2, 7))
# b5 = SecondQuadrant("b5", "a", (-6, 2))
# b6 = SecondQuadrant("b6", "a", (-5.6, 10))
# b7 = SecondQuadrant("b7", "a", (-10, 1))
#
# c = FourthQuadrant("c", "a", (10, -3))
# c2 = FourthQuadrant("c2", "a", (10.1, -3.1))
#
# d = ThirdQuadrant("d", "a", (-10, -10))
# d1 = FourthQuadrant("d1", "a", (1, -10))

# print(d.find_playlist(d1))

# print(b.getQuadrantList())
#
# print(a.first_list)



# angle practice
# x1 = 2
# x2 = -5
# y1 = 3
# y2 = -6
#
# x3 = 2
# x4 = -5
# y3 = 3
# y4 = -7
#
# dy = y2 - y1
# dx = x2 - x1
#
# dy2 = y4 - y3
# dx2 = x4 - x3
#
# value = math.degrees(math.atan2(dy, dx))
# value2 = math.degrees(math.atan2(dy2, dx2))
# print(value)
# print(value2)
