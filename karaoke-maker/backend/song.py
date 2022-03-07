from typing import Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=False)
class Song:
    raw_track_meta: dict[str, Any]
    youtube_link: str
    lyrics: Optional[str]
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
        
        
    def create_file_name(self,base:str="karaoke-maker/data/downloads/") -> str:
        """creates a filename for the song object"""
        
        if not isinstance(base,str):
            raise ValueError("base has to be of type sting")
        base_path = Path(base)
        base_path.mkdir(parents=True,exist_ok=True)
        
        artists = self.contributing_artists
           
        artist_string = artists[0]
        for artist in artists[1:]:
            if artist.lower() not in self.song_name.lower():
                artist_string += "-" + artist
        artist_string = artist_string.replace(".","")
        song_name = self.song_name.replace(".","")
        if self.format is None or self.format == "":
            self.format = "wav"
        converted_file_name = f"{base}{artist_string}-{song_name}.{self.format}"
        total_length = len(converted_file_name)
        if total_length > 100:
            #determine overlap
            cut_off = total_length - 100
            main_artist = artists[0]
            if len(artist_string)-len(main_artist)>=cut_off:
                converted_file_name = f"{base}{main_artist}-{song_name}.{self.format}"
            elif len(artist_string) > cut_off:
                converted_file_name = f"{base}{song_name}.{self.format}"
            elif len(song_name) > 30:
                song_name = song_name[:15]
                converted_file_name = f"{base}{song_name}.{self.format}"
                
            
        # remove characters
        converted_file_name = (
            converted_file_name.replace("/?\\*|<>", "")
            .replace('"', "'")
            .replace(":", "-")
        )
        
        assert len(converted_file_name)<255, "filename is too long"
        

        return converted_file_name
