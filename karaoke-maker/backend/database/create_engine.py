import sqlalchemy
from .models import create_db_schema, DBSong
# create a sqlalchemy engine
def create_db_engine():
    """Create a sqlalchemy engine"""
    engine = sqlalchemy.create_engine(
        "sqlite:///karaoke-maker/data/songs.db",
        connect_args={"check_same_thread": False},
    )
    create_db_schema(engine)
    return engine

   
