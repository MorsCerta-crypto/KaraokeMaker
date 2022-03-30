"""
find song if already downloaded in filesystem
"""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional, Union
import pickle
from utils import Song


@dataclass
class DownloadedSongs:
    def __init__(self, songs_path: str = "karaoke-maker/data/downloads/"):
        if songs_path.endswith(".txt"):
            self.songs_path = Path(songs_path)
        else:
            self.songs_path = Path(songs_path) / "downloads.txt"

    def handle_download_success(self, song: Song):
        """stores an song-path-pair if download was successfully"""
        if not isinstance(song, Song):
            print("wrong type")
            raise TypeError("parameter 'song' has to be of type 'Song'")
        
        if song is not None:
            print("adding song to file : ", song.song_name)
            self.add_songs_to_file(song)
        else:
            print("song is none")
            raise ValueError("song_name and song_path must not be empty")

    def path_in_file(self, path: Union[str,Path]) -> bool:
        """returns true if path matches a path in file"""
        if isinstance(path,str):
            path = Path(path)
        if not isinstance(path,Path):
            raise TypeError("parameter 'path' has to be a string or Path")
        self.song_path = path  # store for later
        downloaded_songs = self.read_songs_from_file()
        if not downloaded_songs:
            # no downloads
            return False
        for song in downloaded_songs:
            if path == song.file_path:
                return True
        return False

    def song_path_from_name(self,name) -> Optional[Path]:
        """returns a path if song name was found in file"""
        songs = self.read_songs_from_file()
        if not songs:
            print("found no songs")
            return None
        print(f"found {len(songs)} in file")
        
        for song in songs:
            if name in song.song_name:
                return song.file_path

    def read_songs_from_file(self) -> list[Song]:
        """reads file given by config param and returns song objects in it"""
        if not self.songs_path.parent.is_dir():
            self.songs_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.songs_path.is_file():
            print(f"making file {self.songs_path}")
            open(self.songs_path,"wb").close()
        if os.path.getsize(self.songs_path) > 0:     
            with open(self.songs_path,"rb") as f:
                unpickler = pickle.Unpickler(f)
                songs = unpickler.load()
                if not isinstance(songs,list):
                    songs = [songs]
                print(f"found {len(songs)} songs")
                # delete duplicates
                another_songs_list = list()
                for song in songs:
                    if song in another_songs_list:
                        print("found duplicate in file")
                        self.remove_song_from_file(song,file=False,current_songs=songs)
                    else:
                        another_songs_list.append(song)
                return songs
        print("found empty file")
        return []

    def songs_in_folder(self)->list[str]:
        """returns a list of all songs found in the folders"""
        songs = []
        path = self.songs_path.parent
        for file in path.iterdir():
            if file.suffix in [".mp3",".wav",".ogg"]:
                songs.append(str(file))
        
        print(f"found {len(songs)} songs as mp3 files")
        return songs
    
    def song_from_path(self,path:Path)->Optional[Song]:
        """compares a path to the paths of song-paths that are stored in the downloads file"""
        songs = self.read_songs_from_file()
        for song in songs:
            if song.file_path == path:
                return song
            
    def remove_song_from_file(self,song:Song,file:bool=False,current_songs:Optional[list[Song]]=None) -> None:
        """removes a song obj from downloads file"""
        
        print("removing song from file: ", song.file_path)
        available_paths:list[str] = self.songs_in_folder()
        if song in available_paths and file:
            print("removing ", song.file_path," from downloads")
            song.file_path.unlink()
        if not current_songs:
            current_songs:list[Song] = self.read_songs_from_file()
        if song in current_songs:
            current_songs.remove(song)
            
        with open(self.songs_path, "wb") as fp:
            pickle.dump(current_songs, fp)
        
        
    def add_songs_to_file(self,song:Song) -> None:
        """if a song was searched add it  file, if downloading was a success, add it to the song list

        Args:
            song (Song): obj of the currently searched song
        """
        print("adding song to file: ", song.file_path)
        if not isinstance(song,Song):
            print("wrong type of song")
            raise TypeError("'song' argument must be of type 'Song'")
        
        #load all availble songs from folder
        available_paths:list[str] = self.songs_in_folder()
        current_songs:list[Song] = self.read_songs_from_file()
        
        #make sure a list is created
        if not current_songs:
            current_songs = [song]
        else: current_songs.append(song)
        #add only available songs
        count = 0
        duplicates = []
        for song in current_songs:
            #dont add a song twice
            
            if song.file_path not in available_paths:
                print("song not available: ", song.file_path," would remove it")
                #current_songs.remove(song)
                count += 1
            else:
                if song in duplicates:
                    print("found duplicate")
                    self.remove_song_from_file(song,file=False)
                else:
                    duplicates.append(song)
            
        if count > 0:
            print(f"Had to drop {count} songs, because they were not found in file {self.songs_path}") 
        
        names = ", ".join([song.song_name for song in current_songs])
        print(f"writing {names} to file")
        with open(self.songs_path, "wb") as fp:
            pickle.dump(current_songs, fp)
        

        