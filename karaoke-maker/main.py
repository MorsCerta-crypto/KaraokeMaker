from src.search.song_search import Search
from src.download.downloader import Downloader

from src.vocalremover.vocalremover import VocalRemover
from src.lyrics.lyrics import SongLyrics

CONFIG = {
    "song_format": "mp3",
    "output_path": "karaoke-maker/data/downloads/",
    "ytdl_format": "bestaudio/best",
}


def run_project(term):

    # search = Search(
    #     output_format=CONFIG["song_format"], songs_path=CONFIG["output_path"]
    # )
    # song = search.from_search_term(term)
    # if song is None:
    #     raise ValueError("song was not found")
    # print("song was found...")

    # downloader = Downloader(
    #     format=CONFIG["song_format"],
    #     output_path=CONFIG["output_path"],
    #     ytdl_format=CONFIG["ytdl_format"],
    # )
    # path = downloader.download_song(song)
    # if path is None:
    #     raise ValueError("song could not be downloaded/found")
    # print("song was downloaded to ", path)

    # remover = VocalRemover()
    # remover.remove_vocals(path)
    
    lyrics = SongLyrics()
    lyrics_text = lyrics.get_lyrics_by_song_name(term)
    print(lyrics_text)
    lyrics.on_success()
    
    


if __name__ == "__main__":
    term = "nightlife - off with their heads"
    run_project(term)
