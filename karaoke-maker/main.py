
from gui import run_gui
import json


def read_config():
    with open("karaoke-maker/karaoke-config.json", "r") as f:
        config = json.load(f)
        return config

def run_project():
    """runs project via interface or with normal commands"""
    config = read_config()
    run_gui(config)
    

if __name__ == "__main__":
    
    run_project()
