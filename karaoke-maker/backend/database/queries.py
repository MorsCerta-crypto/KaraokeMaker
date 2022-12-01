

from models import Song
import sqlalchemy as db


def search_id(id:str, session:db.orm.Session):
    search = db.select(Song).where(Song.id == id)
    for song in session.scalars(search):
        return song
    
def search_name(name:str, session:db.orm.Session):
    search = db.select(Song).where(Song.song_name == name)
    for song in session.scalars(search):
        return song
    
def search_artist(artist:str, session:db.orm.Session):
    search = db.select(Song).where(Song.artist_name == artist)
    for song in session.scalars(search):
        return song

def search_path(path:str, session:db.orm.Session):
    search = db.select(Song).where(Song.path == path)
    for song in session.scalars(search):
        return song

