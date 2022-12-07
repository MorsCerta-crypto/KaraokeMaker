from pathlib import Path
from typing import Optional, Union
import uuid
from spotipy import Spotify # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials # type: ignore
from ..lyrics import SongLyrics
from . import yt_search
from utils import Song


class Search:
    def __init__(self, config:dict):
        self.spotify_client = Spotify(
            client_credentials_manager=SpotifyClientCredentials()
        )

        self.output_format = config["song_format"]
        self.songs_path = config["songs_path"]
        
    def from_search_term(self, query: str) -> Optional[Song]:
        """tries to find a song on spotify with a given searchterm

        Args:
            query (str): searchterm

        Raises:
            Exception: If something in the search-process goes wrong

        Returns:
            list[Song]: found songs
        """
  
        # matches from spotify
        result = self.spotify_client.search(query, type="track")
        # return first result link or if no matches are found, raise Exception
        if result is None or len(result.get("tracks", {}).get("items", [])) == 0:
            raise ValueError("No song matches found on Spotify")
        
        song_url = "http://open.spotify.com/track/" + result["tracks"]["items"][0]["id"]
        
        try:
            song = self.from_spotify_url(song_url)
        except (LookupError, ValueError) as e:
            print("Error occured in search: ", e)
            raise e
        return song
    
    def from_spotify_url(self, spotify_url: str) -> Song:
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
        song_obj = Song(meta_data=raw_track_meta, 
                        youtube_link=youtube_link, 
                        artist_name=artist,
                        id = self.generate_unique_id(),
                        lyrics=lyrics,
                        song_name=song_name, 
                        format=self.output_format)
        return song_obj

    def get_metadata_from_url(self, spotify_url: str)->Optional[dict]:
        """gets metadata from a spotify url"""
        if "open.spotify.com" not in spotify_url or "track" not in spotify_url:
            raise Exception(f"passed URL is not that of a track: {spotify_url}")
        raw_track_meta = self.spotify_client.track(spotify_url)
        return raw_track_meta
    
    def generate_unique_id(self):
        """ generates a unique id for a song """
        return str(uuid.uuid4())

