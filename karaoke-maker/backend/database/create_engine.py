import sqlalchemy
from models import create_db_schema, Song
# create a sqlalchemy engine
def create_engine():
    """Create a sqlalchemy engine"""
    engine = sqlalchemy.create_engine(
        "sqlite:///songs.db",
        connect_args={"check_same_thread": False},
    )
    create_db_schema(engine)
    return engine



if __name__ == "__main__":
    e = create_engine()
    # with sqlalchemy.orm.Session(e) as session:
    #     spongebob = Song(
    #         song_name="spongebob",
    #         id="2",
    #     )
    #     sandy = Song(
    #         song_name="sandy",
    #         id="1"
    #     )
    #     patrick = Song(song_name="patrick", id="3")
    #     session.add_all([spongebob, sandy, patrick])
    #     session.commit()
    
    
    session = sqlalchemy.orm.Session(e)
    
    search = sqlalchemy.select(Song).where(Song.id == 1)
    for song in session.scalars(search):
        print(song)


