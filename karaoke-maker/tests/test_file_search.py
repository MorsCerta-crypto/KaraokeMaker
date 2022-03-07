import pickle
import unittest
from backend.search.file_search import DownloadedSongs
from pathlib import Path
from backend.song import Song

class TestDownloadedSongs(unittest.TestCase):
    def test_read_songs_file_creation(self):
        """test if file gets created"""
        
        songs_path = Path("karaoke-maker/data/downloads/downloads.txt")
        downloads = DownloadedSongs()
        
        #Test 1: make sure file gets created
        _ = downloads.read_songs_from_file()
        file_exists = songs_path.is_file()
        self.assertTrue(file_exists)
    
    def test_read_songs_return_type(self):   
        """single song gets dumped in file"""
        #Test 2: make sure return type is list when given single song
        songs_path = Path("karaoke-maker/data/downloads/downloads.txt")
        downloads = DownloadedSongs()
        
        songs_path.unlink()
        song_single = Song(raw_track_meta={"meta":"data","artists":[{"name":"a"},{"name":"b"}]},youtube_link="link",lyrics="lyrics",song_name="name",format="format")
        with open(songs_path,"wb") as f:
            pickle.dump(song_single,f)
        
            
        with open(songs_path,"rb") as f:
            answer = [pickle.load(f)]
        
        test_answer = downloads.read_songs_from_file()
        
        self.assertTrue(isinstance(test_answer,list),"answer must always be list")
        self.assertEqual(test_answer[0],song_single,"types do not match")
        self.assertEqual(test_answer,answer)
    
    def test_read_songs_return_type_list(self):    
        """list of songs gets dumped in file"""
        #Test 3: make sure return type is list given a list of songs
        songs_path = Path("karaoke-maker/data/downloads/downloads.txt")
        downloads = DownloadedSongs()
        
        songs_path.unlink()
        #now dump list of songs
        song_list = [Song(raw_track_meta={"meta":"data","artists":[{"name":"a"},{"name":"b"}]},youtube_link="link",lyrics="lyrics",song_name="name",format="format")]
        with open(songs_path,"wb") as f:
            pickle.dump(song_list,f)
            
        with open(songs_path,"rb") as f:
            answer = pickle.load(f)
        
        test_answer = downloads.read_songs_from_file()
        
        self.assertTrue(isinstance(test_answer,list),"answer must always be a list")
        self.assertEqual(test_answer,song_list,"type of song is wrong")
        self.assertEqual(test_answer,answer)
        
    def test_add_songs_to_file(self): 
        
        songs_path = Path("karaoke-maker/data/downloads/downloads.txt")
        downloads = DownloadedSongs()   
        song = Song(raw_track_meta={"meta":"data","artists":[{"name":"a"},{"name":"b"}]},youtube_link="link",lyrics="lyrics",song_name="name",format="format")
        if songs_path.is_file():
            songs_path.unlink()
        downloads.add_songs_to_file(song)
        self.assertTrue(songs_path.is_file())
        
        self.assertRaises(TypeError,lambda:downloads.add_songs_to_file("song"))
        self.assertRaises(TypeError,lambda:downloads.add_songs_to_file(11))
        self.assertRaises(TypeError,lambda:downloads.add_songs_to_file({"song":2}))
        
    
    def test_add_songs_to_file_only_available(self):
        """make sure no songs gets added if it does not exist"""
        songs_path = Path("karaoke-maker/data/downloads/downloads.txt")
        downloads = DownloadedSongs()   
        song = Song(raw_track_meta={"meta":"data","artists":[{"name":"a"},{"name":"b"}]},youtube_link="link",lyrics="lyrics",song_name="name",format="format")

        # path does not exist
        self.assertFalse(Path(song.create_file_name()).is_file())
        #make sure only availbale songs get added
        with open(songs_path,"rb") as f:
            songs_in_file_before = pickle.load(f)
        
        downloads.add_songs_to_file(song)
        
        with open(songs_path,"rb") as f:
            songs_in_file_after = pickle.load(f)
        
        self.assertEqual(songs_in_file_before,songs_in_file_after)
        
    
    def test_songs_in_folder(self):
        downloads = DownloadedSongs() 
        songs = downloads.songs_in_folder()
        if songs is not None:
            for song in songs:
                self.assertTrue(song.split(".")[-1] in [".mp3",".wav"],"no correct ending for a song")
                self.assertTrue(Path(song).is_file(),"song has to be a real file")
    
    
    def test_path_in_file_random_inputs(self):
        
        downloads = DownloadedSongs() 
        self.assertRaises(TypeError,lambda:downloads.path_in_file(5))
        self.assertRaises(TypeError,lambda:downloads.path_in_file([2,""]))
        self.assertFalse(downloads.path_in_file(""))
        self.assertFalse(downloads.path_in_file("-"))
    
    def test_path_in_file_correct_inputs(self):
        downloads = DownloadedSongs() 
        correct_paths = downloads.read_songs_from_file()
        if correct_paths is not None and len(correct_paths) > 0:
            self.assertTrue(downloads.path_in_file(correct_paths[0]))
        
            self.assertRaises(TypeError,lambda:downloads.path_in_file(correct_paths))