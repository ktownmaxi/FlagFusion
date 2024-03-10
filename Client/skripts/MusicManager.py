import os
import random


class MusicManager:
    """
    A class to manage the music which is played in the game
    """

    @staticmethod
    def get_song_list(song_path: str) -> list:
        """
        Method to get a song from a directory on the disk
        :param song_path: A Path to the directory where the songs should be chosen form
        :return: A list with the songs
        """
        list_of_songs = os.listdir(song_path)
        return list_of_songs

    def get_next_song(self) -> str:
        """
        Gets the next random song
        :return: Returns the chosen song
        """
        path = os.path.join('../assets/music')
        song_list = self.get_song_list(path)
        f_song = random.choice(song_list)
        return f_song
