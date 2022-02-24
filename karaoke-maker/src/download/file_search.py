"""
find song if already downloaded in filesystem
"""

from dataclasses import dataclass
from typing import Optional, Union
import pickle


@dataclass
class DownloadedSongs:
    def __init__(self, songs_path: str = "/data/songs/"):
        self.songs_path = songs_path + "downloads.txt"
        self.song_name = ""
        self.song_path = ""

    def handle_download_success(self):
        """stores an song-path-pair if download was successfully"""
        if self.song_name != "" and self.song_path != "":
            self.add_songs_to_file()
        else:
            raise ValueError("song_name and song_path must not be empty")

    def path_in_file(self, path: str) -> bool:
        """returns true if path matches a path in file"""
        self.song_path = path  # store for later
        downloaded_songs = self.read_songs_from_file()
        if not downloaded_songs:
            # no downloads
            return False
        if path in downloaded_songs.values():
            ind = list(downloaded_songs.values()).index(path)
            self.song_name = list(downloaded_songs.keys())[ind]
            return True
        return False

    def search_song(self, song_name: str) -> Optional[str]:
        """searches song name first in directory then on spotify

        Args:
            song_name (str): name for a song, spelling is important

        Returns:
            str: path where song is / will be
        """
        self.song_name = song_name  # store for later
        maybe_path = self.song_path_from_name()  # check if song is in downloads
        if maybe_path:
            return maybe_path

    def song_path_from_name(self) -> Union[str, None]:
        """returns a path if song name was found in file"""
        songs = self.read_songs_from_file()
        if not songs:
            return None
        if self.song_name in songs.keys():
            return songs[self.song_name]
        else:
            return None

    def read_songs_from_file(self) -> Union[dict, None]:
        with open(self.songs_path, "rb") as fp:
            songs = pickle.load(fp)
        return songs

    def add_songs_to_file(self) -> None:
        """if a song was searched add it to a temp file, if downloading was a success, add it to the song list

        Args:
            song_name (str): name of the currently searched song
            song_path (str): path where the download will go
        """
        current_songs = self.read_songs_from_file()
        if not current_songs:
            current_songs = dict()
        current_songs[self.song_name] = self.song_path

        with open(self.songs_path, "wb") as fp:
            pickle.dump(current_songs, fp)
