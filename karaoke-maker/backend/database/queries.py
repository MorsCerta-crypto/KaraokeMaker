

from models import Song
import sqlalchemy as db


def search_id(id:str, session:db.orm.Session):
    """ Search for a song by its id"""
    search = db.select(Song).where(Song.id == id)
    for song in session.scalars(search):
        return song
    
def search_name(name:str, session:db.orm.Session):
    """ Search for a song by its name"""
    search = db.select(Song).where(Song.song_name == name)
    for song in session.scalars(search):
        return song
    
def search_artist(artist:str, session:db.orm.Session):
    """ Search for a song by its artist"""
    search = db.select(Song).where(Song.artist_name == artist)
    for song in session.scalars(search):
        return song

def search_path(path:str, session:db.orm.Session):
    """ Search for a song by its path"""
    search = db.select(Song).where(Song.path == path)
    for song in session.scalars(search):
        return song

def get_all_ids(session:db.orm.Session):
    """ Get all the ids of the songs in the database"""
    search = db.select(Song.id)
    return session.scalars(search)

def delete_song(id:str, session:db.orm.Session)->bool:
    """ Delete a song from the database"""
    search = db.select(Song).where(Song.id == id)
    for song in session.scalars(search):
        session.delete(song)
        session.commit()
        return True
    return False

def truncate_database(session:db.orm.Session, really:bool=False):
    """ Delete all the songs from the database"""
    if not really:
        raise Exception("You must set really=True to truncate the database")
    search = db.select(Song)
    for song in session.scalars(search):
        session.delete(song)
    session.commit()

