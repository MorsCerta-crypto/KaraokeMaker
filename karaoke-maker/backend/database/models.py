"""
In this file database models are defined
"""
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()
# definde a sqlalchemy model for the song table with song_name,artist_name,id,path and metadata
class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    song_name = Column(String)
    artist_name = Column(String)
    path = Column(String)
    meta_data = Column(String)
    lyrics = Column(String)
    youtube_link = Column(String)
    format = Column(String)
    duration = Column(Float)
    contributing_artists = Column(String)
    display_name = Column(String)
    file_path = Column(String)
    def __repr__(self):
        return f"""Song(id={self.id}, 
                    song_name={self.song_name}, 
                    artist_name={self.artist_name}, 
                    path={self.path}, 
                    format={self.format}"""
                    
                    
def create_db_schema(engine):
    Base.metadata.create_all(engine)