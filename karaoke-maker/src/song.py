from typing import Optional, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=False)
class Song:
    raw_track_meta: dict[str, Any]
    youtube_link: str
    lyrics: str
    song_name:str
    format: str = "wav"


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
        """returns songs's display name"""
        return str(", ".join(self.contributing_artists) + " - " + self.song_name)

    @property
    def file_path(self)->Path:
        if not self.format or not self.song_name or not self.contributing_artists:
            raise ValueError("Not enough information available for this song")
        return Path(self.create_file_name())
        
        
    def create_file_name(self,short:bool=False) -> str:
        base = "karaoke-maker/data/downloads/"
        artists = self.contributing_artists
        if short:
            artists = artists[:1]
        artist_string = artists[0]
        for artist in artists[1:]:
            if artist.lower() not in self.song_name.lower():
                artist_string += "-" + artist
        artist_string = artist_string.replace(".","")
        song_name = self.song_name.replace(".","")
        if self.format:
            converted_file_name = f"{base}{artist_string}-{song_name}.{self.format}"
        else:
            converted_file_name = f"{base}{artist_string}-{song_name}"
        # remove characters
        converted_file_name = (
            converted_file_name.replace("/?\\*|<>", "")
            .replace('"', "'")
            .replace(":", "-")
        )
        return converted_file_name
