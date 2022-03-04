"""
find song if already downloaded in filesystem
"""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional
import pickle
from ..song import Song


@dataclass
class DownloadedSongs:
    def __init__(self, songs_path: str = "karaoke-maker/data/downloads/"):
        self.songs_path = Path(songs_path) / "downloads.txt"
        self.song = None

    def handle_download_success(self, song: Song):
        """stores an song-path-pair if download was successfully"""
        if song is not None:
            self.add_songs_to_file(song)
        else:
            raise ValueError("song_name and song_path must not be empty")

    def path_in_file(self, path: str) -> bool:
        """returns true if path matches a path in file"""
        self.song_path = path  # store for later
        downloaded_songs = self.read_songs_from_file()
        if not downloaded_songs:
            # no downloads
            return False
        for song in downloaded_songs:
            if path == song.file_path:
                self.song = song
                return True
        return False

    def song_path_from_name(self,name) -> Optional[str]:
        """returns a path if song name was found in file"""
        songs = self.read_songs_from_file()
        if not songs:
            return None
        for song in songs:
            if name in song.song_name:
                return song.file_path

    def read_songs_from_file(self) -> Optional[list]:
        
        self.songs_path.parent.mkdir(parents=True, exist_ok=True)
        
        if os.path.getsize(self.songs_path) > 0:     
            with open(self.songs_path,"rb") as f:
                unpickler = pickle.Unpickler(f)
                songs = unpickler.load()
                return songs

    def songs_in_folder(self)->list[str]:
        songs = []
        path = self.songs_path.parent
        for file in path.iterdir():
            if file.suffix in [".mp3",".wav",".ogg"]:
                songs.append(str(file))
        return songs
        

    def add_songs_to_file(self,song) -> None:
        """if a song was searched add it to a temp file, if downloading was a success, add it to the song list

        Args:
            song (Song): obj of the currently searched song
            
        """
        
        available_songs = self.songs_in_folder()
        current_songs = self.read_songs_from_file()
        len_start = len(current_songs)
        if current_songs:
            current_songs.append(song)
        else: current_songs = [song]
        for index,song in enumerate(current_songs):
            if song.file_path in available_songs:
                current_songs.remove(index)
        print("deleted :", len(current_songs)-len_start)
        with open(self.songs_path, "wb") as fp:
            pickle.dump(current_songs, fp)
