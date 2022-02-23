from typing import Optional,Any
from dataclasses import dataclass

@dataclass
class Song:
    raw_track_meta:dict[str,Any]
    youtube_link:str
    lyrics:str
    playlist:dict[str,str]
    

    @property
    def song_name(self) -> str:
        """returns songs's name"""
        return self.raw_track_meta["name"]

    @property
    def duration(self) -> float:
        """returns duration of song in seconds"""
        return round(self.raw_track_meta["duration_ms"] / 1000, ndigits=3)

    @property
    def contributing_artists(self) -> list[str]:
        """returns a list of all artists who worked on the song"""
        return [artist["name"] for artist in self.raw_track_meta["artists"]]

    @property
    def display_name(self) -> str:
        """ returns songs's display name """

        return str(", ".join(self.contributing_artists) + " - " + self.song_name)

    @property
    def file_name(self) -> str:
        return self.create_file_name(
            song_name=self.raw_track_meta["name"],
            song_artists=[artist["name"] for artist in self.raw_track_meta["artists"]],
        )

    @staticmethod
    def create_file_name(song_name: str, song_artists: list[str]) -> str:

        artist_string = song_artists[0]
        for artist in song_artists[1:]:
            if artist.lower() not in song_name.lower():
                artist_string += ", " + artist

        converted_file_name = f"{artist_string}-{song_name}"

        # remove characters
        converted_file_name = (
            converted_file_name.replace("/?\\*|<>", "")
            .replace('"', "'")
            .replace(":", "-")
        )
        return converted_file_name
