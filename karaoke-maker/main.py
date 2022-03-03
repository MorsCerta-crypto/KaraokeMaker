
from src.gui.interface import run_gui
import json


def read_config():
    with open("karaoke-maker/karaoke-config.json", "r") as f:
        config = json.load(f)
        return config

def run_project():
    """runs project via interface or with normal commands"""
    config = read_config()
    # term = input("enter song name\n")
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
    
    run_gui(config)
    

if __name__ == "__main__":
    
    run_project()
