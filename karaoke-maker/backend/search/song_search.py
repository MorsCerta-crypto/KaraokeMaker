from pathlib import Path
from typing import Optional, Union
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from ..lyrics import SongLyrics
from . import yt_search
from utils import Song
from .file_search import DownloadedSongs

class Search:
    def __init__(self, config:dict):
        self.spotify_client = Spotify(
            client_credentials_manager=SpotifyClientCredentials()
        )

        self.output_format = config["song_format"]
        self.songs_path = config["songs_path"]
        self.file_search = DownloadedSongs(config["songs_path"])

    def from_search_term(self, query: str) -> Optional[Union[Path,Song]]:
        """tries to find a song on spotify with a given searchterm

        Args:
            query (str): searchterm

        Raises:
            Exception: If something in the search-process goes wrong

        Returns:
            list[Song]: found songs
        """
        print("searching for ", query)
        # matches from spotify
        result = self.spotify_client.search(query, type="track")
        # return first result link or if no matches are found, raise Exception
        if result is None or len(result.get("tracks", {}).get("items", [])) == 0:
            raise Exception("No song matches found on Spotify")
        
        song_url = "http://open.spotify.com/track/" + result["tracks"]["items"][0]["id"]
        
        try:
            song = self.from_spotify_url(song_url)
        except (LookupError, ValueError) as e:
            print("Error occured in search: ", e)
            raise e
        return song
    
    def from_spotify_url(self, spotify_url: str) -> Union[Song,Path]:
        """finds a song on spotify with a given song-url

        Args:
            spotify_url (str): url of a song on spotify

        Raises:
            ValueError: no metadata was found for this song
            OSError: this file was already downloaded
            LookupError: no match on youtube was found

        Returns:
            Song: Song object
        """
        raw_track_meta = self.get_metadata_from_url(spotify_url)
        
        if raw_track_meta is None:
            raise ValueError("Couldn't get metadata from url")
        #CHECK IF ALREADY DOWNLOADED
        path = Path(Song(raw_track_meta=raw_track_meta,
                    youtube_link = "None", 
                    lyrics= "None", 
                    song_name=raw_track_meta["name"],
                    format=self.output_format).create_file_name())
        
        print("check if path is file: ", path, path.is_file())
        if path.is_file():
            song_obj = self.try_recreate_song_obj(path)
            if song_obj is not None:
                return song_obj
            

        song_name = raw_track_meta["name"]
        isrc = raw_track_meta.get("external_ids", {}).get("isrc",None)
        duration = round(raw_track_meta["duration_ms"] / 1000, ndigits=3)
        contributing_artists = [artist["name"] for artist in raw_track_meta["artists"]]
        youtube_link = yt_search.search_song(
            song_name, contributing_artists, duration, isrc
        )

        # Check if we found youtube url
        if youtube_link is None:
            raise LookupError("no youtube url was found")
        
        
        Lyrics = SongLyrics()
        artist = contributing_artists[0]
        lyrics = Lyrics.get_lyrics_by_artist_and_song(artist_name=artist,song_title=song_name)
        song_obj = Song(raw_track_meta=raw_track_meta, 
                        youtube_link=youtube_link, 
                        lyrics=lyrics,
                        song_name=song_name, 
                        format=self.output_format)
        
        # Create file name
        song_obj.create_file_name()

        return song_obj
     
    def try_recreate_song_obj(self,path:Path):
        song_match = self.file_search.song_from_path(path)
        if song_match is not None and isinstance(song_match, Song):
            return song_match
        return None

    def get_metadata_from_url(self, spotify_url: str)->Optional[dict]:

        if "open.spotify.com" not in spotify_url or "track" not in spotify_url:
            raise Exception(f"passed URL is not that of a track: {spotify_url}")

        raw_track_meta = self.spotify_client.track(spotify_url)
        return raw_track_meta


if __name__ == "__main__":
    config= {"song_format":"wav","song_path":"karaoke-maker/data/downloads"}
    s = Search(config)
    ans = s.from_search_term("ballad of hollywood jack and the rage cage")
    print(ans)
