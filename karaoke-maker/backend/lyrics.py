from typing import Optional
from lyricsgenius import Genius

class SongLyrics:
    def __init__(self):
        self.lyrics_str=""
        self.genius = Genius()
        self.genius.verbose = False #suppress output
        self.genius.remove_section_headers = True #remove headers like chorus
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
            return self.lyrics_str
        return None
        
            
        

