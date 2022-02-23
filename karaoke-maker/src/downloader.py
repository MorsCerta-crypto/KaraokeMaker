import asyncio
import os
from pathlib import Path
from yt_dlp import YoutubeDL
from song import Song


class Downloader:
    def __init__(
        self,
        format: str = "mp3",
        output_path: str = "/data/downloads/",
        ytdl_format: str = "bestaudio",
    ):
        self.format = format
        self.output_path = output_path
        self.ytdl_format = ytdl_format

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
        # make sure artist names are only once in the Path-string
        for artist in song_obj.contributing_artists:
            if artist.lower() not in song_obj.song_name:
                unique_artists.append(artist)
            elif artist.lower() is song_obj.contributing_artists[0].lower():
                unique_artists.append(artist)

        converted_file_name = Song.create_file_name(
            song_obj.song_name, unique_artists, format
        )

        file_path = Path(converted_file_name)
        try:
            if len(str(file_path.resolve().name)) > 256:
                song_obj.contributing_artists = []
                if repeat == False:
                    return self.get_file_path(song_obj, format, repeat=True)
        except OSError:
            song_obj.contributing_artists = []
            if repeat == False:
                return self.get_file_path(song_obj, format, repeat=True)

        return file_path

    def download_song(self, song_object: Song, temp_folder: str, file_path: str):

        converted_file_path = str(self.get_file_path(song_object, self.format).name)
        saving_name = (
            file_path + converted_file_path
            if file_path.endswith("/")
            else file_path + "/" + converted_file_path
        )
        saving_path = Path(saving_name)

        print("converting file to: ", saving_path)
        print("downloading file to: ", file_path)
        saving_path.parent.mkdir(parents=True, exist_ok=True)
        if saving_path.is_file():
            return

        audio_handler = YoutubeDL(
            {
                "format": self.ytdl_format,
                "outtmpl": f"{temp_folder}/%(id)s.%(ext)s",
                "quiet": True,
                "no_warnings": True,
            }
        )

        try:
            downloaded_file_path_string = self.downlaod_audio(
                file_name=file_path.split(".")[0],
                temp_folder=temp_folder,
                audio_handler=audio_handler,
                youtube_link=song_object.youtube_link,
            )
        except Exception as e:
            print(
                f'No audio was downloaded for "{song_object.song_name}", because of {e}'
            )
            return None

        if downloaded_file_path_string is None:
            return None

        downloaded_file_path = Path(str(downloaded_file_path_string))
        print(f"downloaded file to path: {downloaded_file_path}")
        cmd = " ".join(
            [
                "ffmpeg",
                "-i",
                downloaded_file_path_string,
                "-codec:a",
                "libmp3lame",
                "-abr",
                "true",
                "-q:a",
                "0",
                "-v",
                "debug",
                saving_name,
            ]
        )
        os.system(cmd)
        # conversion_success = True if process.returncode == 0 else False
        conversion_success = True
        if conversion_success is False:
            print("no success in converting")
            # delete the file that wasn't successfully converted
            saving_path.unlink()

        # delete downloaded file
        if downloaded_file_path and downloaded_file_path.is_file():
            downloaded_file_path.unlink()

    def downlaod_audio(self, youtube_link, file_name, temp_folder, audio_handler):

        print("youtube_link: ", youtube_link)
        print(file_name)

        try:
            data = audio_handler.extract_info(youtube_link)

            return f"{temp_folder}/{data['id']}.{data['ext']}"
        except Exception as e:

            temp_files = Path(temp_folder).glob(f"{file_name}.*")
            for temp_file in temp_files:
                temp_file.unlink()
            raise e


if __name__ == "__main__":
    artist1 = dict()
    artist2 = dict()
    meta_data = dict()
    artist1["name"] = "John"
    artist2["name"] = "elvis"
    meta_data["name"] = "song_name"
    meta_data["artists"] = [artist1, artist2]

    d = Downloader()
    d.download_song(
        song_object=Song(
            meta_data,
            "https://youtube.com/watch?v=N0hFf-twPlY",
            "heealaaa",
            {"": ""},
        ),
        temp_folder="data/temp",
        file_path="data/downloads/",
    )
