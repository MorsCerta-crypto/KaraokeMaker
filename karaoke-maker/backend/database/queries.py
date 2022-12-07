

from .models import DBSong
import sqlalchemy as db

def search_id(id:str, session:db.orm.Session): # type: ignore
    """ Search for a song by its id"""
    assert isinstance(id, str), "id must be a string"
    assert isinstance(session, db.orm.Session), "Session must be a sqlalchemy.orm.Session" # type: ignore
    search = db.select(DBSong).where(DBSong.id == id)
    for song in session.scalars(search):
        return song
    
def search_name(name:str, session:db.orm.Session): # type: ignore
    """ Search for a song by its name"""
    assert isinstance(name, str), "name must be a string"
    assert isinstance(session, db.orm.Session), "Session must be a sqlalchemy.orm.Session" # type: ignore
    search = db.select(DBSong).where(DBSong.song_name == name)
    for song in session.scalars(search):
        return song
    
def search_artist(artist:str, session:db.orm.Session): # type: ignore
    """ Search for a song by its artist"""
    assert isinstance(artist, str), "artist must be a string"
    assert isinstance(session, db.orm.Session), "Session must be a sqlalchemy.orm.Session" # type: ignore
    search = db.select(DBSong).where(DBSong.artist_name == artist)
    for song in session.scalars(search):
        return song

def search_path(path:str, session:db.orm.Session): # type: ignore
    """ Search for a song by its path"""
    assert isinstance(path, str), "path must be a string"
    assert isinstance(session, db.orm.Session), "Session must be a sqlalchemy.orm.Session" # type: ignore
    search = db.select(DBSong).where(DBSong.path == path)
    for song in session.scalar(search):
        return song

def get_all_ids(session:db.orm.Session): # type: ignore
    """ Get all the ids of the songs in the database"""
    assert isinstance(session, db.orm.Session), "Session must be a sqlalchemy.orm.Session" # type: ignore
    search = db.select(DBSong.id).order_by(DBSong.id)
    return session.scalars(search)

def get_all_songs(session: db.orm.Session): # type: ignore
    """ Get all the songs in the database"""
    assert isinstance(session, db.orm.Session), "Session must be a sqlalchemy.orm.Session" # type: ignore
    ids = get_all_ids(session)
    search = db.select(DBSong).where(DBSong.id.in_(ids))
    return session.scalars(search)

def add_song(song:dict, session:db.orm.Session): # type: ignore
    """ Add a song to the database"""
    assert isinstance(song, dict), "song must be a Song"
    assert isinstance(session, db.orm.Session), "Session must be a sqlalchemy.orm.Session" # type: ignore
    # check if song is already in db
    if search_id(song["id"], session):
        return
    if search_name(song["song_name"], session):
        return
    session.add(DBSong(**song))
    session.commit()

def delete_song(id:str, session:db.orm.Session)->bool: # type: ignore
    """ Delete a song from the database"""
    assert isinstance(id, str), "id must be a string"
    assert isinstance(session, db.orm.Session), "Session must be a sqlalchemy.orm.Session" # type: ignore
    search = db.select(DBSong).where(DBSong.id == id)
    for song in session.scalar(search):
        session.delete(song)
        session.commit()
        return True
    return False

def truncate_database(session:db.orm.Session, really:bool=False): # type: ignore
    """ Delete all the songs from the database"""
    assert isinstance(session, db.orm.Session), "Session must be a sqlalchemy.orm.Session" # type: ignore
    if not really:
        raise Exception("You must set really=True to truncate the database")
    search = db.select(DBSong)
    for song in session.scalars(search):
        session.delete(song)
    session.commit()

