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



if __name__ == "__main__":
    pass
    #e = create_db_engine()
    #with sqlalchemy.orm.Session(e) as session:
    #     spongebob = Song(
    #         songs.id, songs.song_name, songs.artist_name, songs.original_path, songs.instrumentals_path, songs.vocals_path, songs.meta_data, songs.lyrics, songs.youtube_link, songs.format, songs.duration, songs.contributing_artists, songs.display_name
    #     )
    #     sandy = Song(
    #         song_name="sandy",
    #         id="1"
    #     )
    #     patrick = Song(song_name="patrick", id="3")
    #     session.add_all([spongebob, sandy, patrick])
    #     session.commit()
    
    
    # session = sqlalchemy.orm.Session(e) # type: ignore
    
    # search = sqlalchemy.select(Song).where(Song.id == 1)
    # for song in session.scalars(search):
    #     print(song)


