


from pathlib import Path
import unittest
from backend.song import Song

class TestSong(unittest.TestCase):
    
    def test_file_path_correct(self):
        song = Song(raw_track_meta={"meta":"data",
                                    "artists":[{"name":"a_name"},
                                               {"name":"b_name"}]},
                    youtube_link="link",
                    lyrics="lyrics",
                    song_name="name",
                    format="format")
        path = song.file_path
        self.assertTrue(isinstance(path,Path))
    
    def test_file_path_raises(self):
        #no format
        song = Song(raw_track_meta={"meta":"data",
                                    "artists":[{"name":"a_name"},
                                               {"name":"b_name"}]},
                    youtube_link="link",
                    lyrics="lyrics",
                    song_name="",
                    format="")   
        self.assertRaises(ValueError,lambda:song.file_path) 
        
        #no artists
        song = Song(raw_track_meta={"meta":"data",
                                    "artists":[]},
                    youtube_link="link",
                    lyrics="lyrics",
                    song_name="name",
                    format="format")   
        self.assertRaises(ValueError,lambda:song.file_path)
        
        #no name
        song = Song(raw_track_meta={"meta":"data",
                                    "artists":[{"name":"a_name"},
                                               {"name":"b_name"}]},
                    youtube_link="link",
                    lyrics="lyrics",
                    song_name="",
                    format="format")   
        self.assertRaises(ValueError,lambda:song.file_path)
    
    def test_display_name(self):
        pass
        
    def test_contributing_artists(self):
        song = Song(raw_track_meta={"meta":"data",
                                    "artists":[{"name":"a"},
                                               {"name":"b"}]},
                    youtube_link="link",
                    lyrics="lyrics",
                    song_name="long_long_long_long_long_long_long_name",
                    format="format")
        self.assertEqual(song.contributing_artists,["a","b"])
    
    def test_file_name_to_long(self):
        song = Song(raw_track_meta={"meta":"data",
                                    "artists":[{"name":"a_long_long_long_long_name"},
                                               {"name":"b_also_long_long_long_long_name"}]},
                    youtube_link="link",
                    lyrics="lyrics",
                    song_name="long_long_long_long_long_long_long_name",
                    format="format")
        
        self.assertTrue(len(song.create_file_name())<=100)
        
        
    def test_file_name_correct(self):
        song = Song(raw_track_meta={"meta":"data",
                                    "artists":[{"name":"a"},
                                               {"name":"b"}]},
                    youtube_link="link",
                    lyrics="lyrics",
                    song_name="name",
                    format="format")
        
        file_name = song.create_file_name(base="")
        self.assertEqual(file_name,"a-b-name.format")
        
    def test_file_base_creation(self):
        song = Song(raw_track_meta={"meta":"data",
                                    "artists":[{"name":"a"},
                                               {"name":"b"}]},
                    youtube_link="link",
                    lyrics="lyrics",
                    song_name="name",
                    format="format")
        base="karaoke-maker/data2/downloads3/"
        file_name = song.create_file_name(base=base)
        self.assertEqual(file_name,f"{base}a-b-name.format")
        base_path = Path(base)
        self.assertTrue(base_path.is_dir())
        