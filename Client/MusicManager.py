import random
import os


class MusicManager:

    @staticmethod
    def get_song_list(song_path):
        list_of_songs = os.listdir(song_path)
        return list_of_songs

    def get_next_song(self):
        path = os.path.join('assets/music')
        song_list = self.get_song_list(path)
        f_song = random.choice(song_list)
        return f_song
