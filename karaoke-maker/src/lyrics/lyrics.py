import os
from pathlib import Path
from typing import Optional
from lyricsgenius import Genius


class SongLyrics:
    def __init__(self):
        self.lyrics_str=""
        self.export_dir = Path("/karaoke-maker/data/lyrics/")
        #if not os.path.exists(self.export_dir):
        #    os.makedirs(self.export_dir)
        self.genius = Genius()
        # Turn off status messages
        self.genius.verbose = False

        # Remove section headers (e.g. [Chorus]) from lyrics when searching
        self.genius.remove_section_headers = True

        # Include hits thought to be non-songs (e.g. track lists)
        self.genius.skip_non_songs = False

        # Exclude songs with these words in their title
        # genius.excluded_terms = ["(Remix)", "(Live)"]

    def get_lyrics_by_song_name(self, song_title: str) -> Optional[str]:
        """find the song by its title"""
        song = self.genius.search_song(title=song_title)
        if song:
            self.song_name = song.full_title.encode("ascii", "ignore").decode()
            self.lyrics_str = song.to_text()
            return song.lyrics

    def get_song_name_by_lyrics(self, lyrics_term: str) -> list[str]:
        """find the song name from lyrics"""
        song_names = []
        request = self.genius.search_lyrics(lyrics_term)
        for hit in request["sections"][0]["hits"]:
            song_names.append(hit["result"]["title"])
        return song_names

    def get_lyrics_by_artist_and_song(self, artist_name: str, song_title: str) -> Optional[str]:
        """find the lyrics for a song with a known artist"""
        # artist = self.genius.search_artist(artist_name, max_songs=1)

        song = self.genius.search_song(title=song_title, artist=artist_name)
        if song:
            self.song_name = song.full_title.encode("ascii", "ignore").decode()
            self.lyrics_str =  song.to_text()
            return song.to_text()
        
    def on_success(self):
        name = self.song_name+".txt"
        path = self.export_dir/name
        if self.lyrics_str == "" or self.lyrics_str is None:
            raise ValueError("lyrics are empty")
        #if not os.path.exists(path):
        #    os.makedirs(path)
        with open(path,"w+") as f:
            f.write(self.lyrics_str)
            
        

