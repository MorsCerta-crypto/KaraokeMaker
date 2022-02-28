from lyricsgenius import Genius


class SongLyrics:
    def __init__(self):
        self.genius = Genius
        # Turn off status messages
        self.genius.verbose = False

        # Remove section headers (e.g. [Chorus]) from lyrics when searching
        self.genius.remove_section_headers = True

        # Include hits thought to be non-songs (e.g. track lists)
        self.genius.skip_non_songs = False

        # Exclude songs with these words in their title
        # genius.excluded_terms = ["(Remix)", "(Live)"]

    def get_lyrics_by_song_name(self, song_title: str) -> str:
        """find the song by its title"""
        song = self.genius.search_song(song_title)
        return song.lyrics

    def get_song_name_by_lyrics(self, lyrics_term: str) -> str:
        """find the song name from lyrics"""
        song_names = []
        request = self.genius.search_lyrics(lyrics_term)
        for hit in request["sections"][0]["hits"]:
            song_names.append(hit["result"]["title"])
        return song_names

    def get_lyrics_by_artist_and_song(self, artist_name: str, song: str) -> str:
        """find the lyrics for a song with a known artist"""
        # artist = self.genius.search_artist(artist_name, max_songs=1)

        search_song = self.genius.search_song(song, artist_name)
        return search_song.lyrics
