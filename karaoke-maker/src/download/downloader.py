from pathlib import Path
from typing import Optional
import youtube_dl
from ..song import Song
from .file_search import DownloadedSongs
from src.lyrics.lyrics import SongLyrics

class Downloader:
    def __init__(
        self,
        config:dict
    ):
    
        self.format = config["song_format"]
        self.output_path = config["output_path"]
        self.ytdl_format = config["ytdl_format"]
        self.downloaded_songs = DownloadedSongs(self.output_path)

    def get_file_path(self, song_obj: Song, format: str, repeat=False) -> Path:
        """generates file Path object from artists and song name and appends the extension

        Args:
            song_obj (Song): Song-object to extract name and artist
            format (str): extension for file
            repeat (bool, optional): used to shorten filename in case its to long. Defaults to False.

        Returns:
            Path: Path object to store file to
        """
        unique_artists = []
        if not repeat:
            # make sure artist names are only once in the Path-string
            for artist in song_obj.contributing_artists:
                if artist.lower() not in song_obj.song_name:
                    unique_artists.append(artist)
                elif artist.lower() is song_obj.contributing_artists[0].lower():
                    unique_artists.append(artist)

        converted_file_name = song_obj.create_file_name()

        file_path = Path(converted_file_name)
        try:
            if len(str(file_path.resolve().name)) > 256:
                if repeat == False:
                    return self.get_file_path(song_obj, format, repeat=True)
        except OSError:
            if repeat == False:
                return self.get_file_path(song_obj, format, repeat=True)

        return file_path

    def download_song(
        self,
        song_object: Song,
        file_path: str = "karaoke-maker/data/downloads/",
    ) -> Optional[str]:
        """downloads a given song if it is not in file system

        Args:
            song_object (Song): song object that sould be downloaded
            file_path (str): filepath to store the final file

        Retruns:
            str: Path of the downloaded file
        """
        converted_file_path = str(self.get_file_path(song_object, self.format).name)
        saving_name = (
            file_path + converted_file_path
            if file_path.endswith("/")
            else file_path + "/" + converted_file_path
        )
        saving_path = Path(saving_name)

        # saving_path.parent.mkdir(parents=True, exist_ok=True)
        if saving_path.is_file():
            return saving_name

        if self.downloaded_songs.path_in_file(saving_name):
            return saving_name

        options = {
            "format": self.ytdl_format,
            "keepvideo": False,
            "outtmpl": saving_name,
            "noplaylist": True,
            "continue_dl": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.format,
                    "preferredquality": "192",
                }
            ],
        }
        success = False
        try:
            video_info = youtube_dl.YoutubeDL(options).extract_info(
                url=song_object.youtube_link, download=True
            )
            if video_info:
                success = True
        except Exception as e:
            print("download failed ", e)

        if success:
            Lyrics = SongLyrics()
            artist = song_object.contributing_artists[0]
            song_object.lyrics = Lyrics.get_lyrics_by_artist_and_song(artist_name=artist,song_title=song_object.song_name)
            self.downloaded_songs.handle_download_success(song_object)

        return saving_name



if __name__ == "__main__":
    

    d = Downloader()
    d.download_song(
        song_object=None,
        file_path="data/downloads/",
    )
