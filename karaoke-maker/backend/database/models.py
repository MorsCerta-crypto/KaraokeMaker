"""
In this file database models are defined
"""
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()
# definde a sqlalchemy model for the song table with song_name,artist_name,id,path and metadata
class DBSong(Base):
    __tablename__ = "songs"
    # key features of a song
    id = Column(String, primary_key=True)
    song_name = Column(String)
    artist_name = Column(String)
    # Paths for the song
    original_path = Column(String)
    instrumentals_path = Column(String)
    vocals_path = Column(String)
    # Metadata (Optional)
    meta_data = Column(String)
    lyrics = Column(String)
    youtube_link = Column(String)
    format = Column(String)
    duration = Column(Float)
    contributing_artists = Column(String)
    display_name = Column(String)
    
    def __repr__(self):
        return f"""DBSong(id={self.id}, 
                    song_name={self.song_name}, 
                    artist_name={self.artist_name}, 
                    path={self.path}, 
                    format={self.format}"""
                    
                    
def create_db_schema(engine):
    Base.metadata.create_all(engine)