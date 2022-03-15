from pathlib import Path
from typing import Optional
import youtube_dl
from .search import DownloadedSongs
from .lyrics import SongLyrics
from utils import Song


class Downloader:
    def __init__(
        self,
        config:dict
    ):
    
        self.format = config["song_format"]
        self.output_path = config["output_path"]
        self.ytdl_format = config["ytdl_format"]
        self.downloaded_songs = DownloadedSongs(self.output_path)


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
            
        saving_name = song_object.create_file_name(file_path)
        saving_path = Path(saving_name)
        
        # saving_path.parent.mkdir(parents=True, exist_ok=True)
        if saving_path.is_file():
            if not self.downloaded_songs.path_in_file(saving_path):
                self.downloaded_songs.handle_download_success(song_object)
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
            
        if success and song_object.lyrics is None:
            # retry getting lyrics
            Lyrics = SongLyrics()
            artist = song_object.contributing_artists[0]
            lyrics = Lyrics.get_lyrics_by_artist_and_song(artist_name=artist,song_title=song_object.song_name)
            song_object.lyrics = lyrics if lyrics is not None else None
            self.downloaded_songs.handle_download_success(song_object)

        return saving_name


