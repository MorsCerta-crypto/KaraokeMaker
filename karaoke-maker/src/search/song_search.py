from pathlib import Path
from typing import Optional
from ..song import Song
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from . import yt_search


class Search:
    def __init__(self, config:dict):
        self.spotify_client = Spotify(
            client_credentials_manager=SpotifyClientCredentials()
        )

        self.output_format = config["output_format"]
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
            raise Exception("No song matches found on Spotify")
        song_url = "http://open.spotify.com/track/" + result["tracks"]["items"][0]["id"]
        try:
            song = self.from_spotify_url(song_url)
            return song if song.youtube_link is not None else None
        except (LookupError, OSError, ValueError):
            return None

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
        isrc = raw_track_meta.get("external_ids", {}).get("isrc")
        duration = round(raw_track_meta["duration_ms"] / 1000, ndigits=3)
        contributing_artists = [artist["name"] for artist in raw_track_meta["artists"]]
        youtube_link = yt_search.search_song(
            song_name, contributing_artists, duration, isrc
        )

        # Check if we found youtube url
        if youtube_link is None:
            raise LookupError("no youtube url was found")
        lyrics = ""
        song_obj = Song(raw_track_meta=raw_track_meta, 
                        youtube_link=youtube_link, 
                        lyrics=lyrics,
                        song_name=song_name, 
                        format=self.output_format)
        # Create file name
        song_obj.create_file_name()
        # If song name is too long remove artists
        if len(str(song_obj.file_path)) > 250:
            song_obj.create_file_name(short=True)
        # if a song is already downloaded skip it
        if song_obj.file_path.is_file():
            raise OSError(f"file already downloaded")
        return song_obj

    def get_metadata_from_url(self, spotify_url: str):

        if "open.spotify.com" not in spotify_url or "track" not in spotify_url:
            raise Exception(f"passed URL is not that of a track: {spotify_url}")

        raw_track_meta = self.spotify_client.track(spotify_url)
        return raw_track_meta


if __name__ == "__main__":
    s = Search()
    ans = s.from_search_term("ballad of hollywood jack and the rage cage")
    print(ans)
