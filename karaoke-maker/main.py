
from gui import run_gui
import json
from backend.database import engine, queries
from sqlalchemy.orm import Session

def read_config():
    with open("karaoke-maker/karaoke-config.json", "r") as f:
        config = json.load(f)
        return config

def run_project():
    """runs project via interface or with normal commands"""
    config = read_config()
    with Session(engine) as session:
        run_gui(config, session, queries)
    
if __name__ == "__main__":
    run_project()
