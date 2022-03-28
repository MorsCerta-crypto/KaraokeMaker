from pathlib import Path
import youtube_dl
from typing import Optional
from .search import DownloadedSongs
from .lyrics import SongLyrics
from utils import Song
from threading import Thread

class Downloader(Thread):
    def __init__(
        self,
        config:dict,song_obj:Optional[Song]
    ):
        super().__init__()
        if song_obj:
            self.song_obj = song_obj
        self.format = config["song_format"]
        self.output_path = config["output_path"]
        self.ytdl_format = config["ytdl_format"]
        self.downloaded_songs = DownloadedSongs(self.output_path)
        self.saving_name = ""

    def run(self)->None:
        """function to be called by thread to download songs"""
        if self.song_obj is not None:
            self.download_song(self.song_obj)

    def download_song(
        self,
        song_object: Song
    ):
        """downloads a given song if it is not in file system

        Args:
            song_object (Song): song object that sould be downloaded
            file_path (str): filepath to store the final file

        Retruns:
            str: Path of the downloaded file
        """
            
        self.saving_name = song_object.create_file_name(self.output_path)
        saving_path = Path(self.saving_name)
        
        # saving_path.parent.mkdir(parents=True, exist_ok=True)
        if saving_path.is_file():
            if not self.downloaded_songs.path_in_file(saving_path):
                self.downloaded_songs.handle_download_success(song_object)
            return 

        options = {
            "format": self.ytdl_format,
            "keepvideo": False,
            "outtmpl": self.saving_name,
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
        
        try:
            video_info = youtube_dl.YoutubeDL(options).extract_info(
                url=song_object.youtube_link, download=True
            )
            print("returned video info: ", video_info)
            
        except Exception as e:
            print("download failed ", e)
            
        if song_object.lyrics is None:
            # retry getting lyrics
            Lyrics = SongLyrics()
            artist = song_object.contributing_artists[0]
            lyrics = Lyrics.get_lyrics_by_artist_and_song(artist_name=artist,song_title=song_object.song_name)
            song_object.lyrics = lyrics if lyrics is not None else None
            
        print("file was successfully stored: ", song_object.song_name)
        self.downloaded_songs.handle_download_success(song_object)

        return 


