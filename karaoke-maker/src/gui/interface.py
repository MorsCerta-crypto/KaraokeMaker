import os
import pickle
from tkinter import *
from typing import Optional
from ..song import Song
from src.gui.music_player import MusicPlayer
from src.gui.lyrics_window import show_lyrics
  
class Interface:
    def __init__(self,root,search_cls,download_cls,lyrics_cls,vocal_remover,downloads_path = "karaoke-maker/data/downloads/downloads.txt"):
        
        self.downloads_path = downloads_path
        self.search_cls = search_cls()
        self.download_cls = download_cls()
        self.lyrics_cls = lyrics_cls()
        self.vocal_remover = vocal_remover()
        
        self.root = root
        self.root.title("Select a Song")
        self.root.geometry("1000x600+200+200")
        self.root.configure(bg='light grey')
        
        self.search_spot_commit = Button(self.root,text = "Search",width=30,fg = 'black',font=('Arial',16,'bold'),command=self.search_song_spotify)
        self.search_loc_commit = Button(self.root,text = "Search",width=30,fg = 'black',font=('Arial',16,'bold'),command=self.search_song_local)
        self.search_spot_commit.grid(column=1,row=0)
        self.search_loc_commit.grid(column=2,row=0)
        text = StringVar()
        self.search_field = Entry(self.root,width=80,textvariable=text)
        self.search_field.grid(column=0,row=0)
        self.Songs = self.load_songs_from_file()
        self.show_songs(self.Songs)
        self.music_player = None
        self.Song = None
        self.display_sons = None
        
    def load_songs_from_file(self)-> list[Song]:
        if not os.path.exists(self.downloads_path):
            os.makedirs(self.downloads_path)
        if os.path.getsize(self.downloads_path) > 0:     
            with open(self.downloads_path,"rb") as f:
                unpickler = pickle.Unpickler(f)
                songs = unpickler.load()
                return songs
        return []
        
    def select_song_by_cursor(self,event):
        """select a song by cursor"""
        index = self.display_songs.curselection()[0]
        name = self.get_song_name_from_repr(self.display_songs.get(index))
        print("name: ",name)
        
        #find a match in all songs
        match_song = None
        for song in self.Songs:
            if song.song_name == name:
                match_song = song
                break
        # no match means error happened
        if not match_song:
            raise ValueError("no match found")
        
        #set self.Song to the currently selected song
        self.Song = match_song
        path = str(self.Song.file_path)
        print("path: ",path)
        if path == []:
            raise ValueError(f"stored no path for this song: {name}")
        basename = os.path.splitext(os.path.basename(path))[0]
        file = f"karaoke-maker/data/backing_tracks/{basename}_Instruments.wav"
        if not os.path.isfile(path):
            #download song if it does not exist
            self.download_song()
        elif not os.path.isfile(file):
            # extract vocals from downloaded song
            self.vocal_remover.remove_vocals(path)
        # play song if its instrumental can be found
        show_lyrics(self.Song.lyrics,self.root)
        print("lyrics")
        if not self.music_player:
            print("no music player")
            self.music_player = MusicPlayer(self.root)
        if not self.music_player.root.state == "normal": #check if music player is active
            print("not active")
            self.music_player = MusicPlayer(self.root)
            
        self.music_player.append_song(file)
        print("appended song to music player: ",file)
            
            
            
        
    def download_song(self):
        """downloads song if it is not in file"""
        if self.Song is not None:
            saving_name = self.download_cls.download_song(self.Song)
            print("saved at: ",saving_name,"now extracting vocals")
            
            self.vocal_remover.remove_vocals(saving_name)

    def search_song_local(self):
        song_str = self.search_field.get()
        max_match_ind = -1
        max_match_val = 0
        
        for ind,song in enumerate(self.Songs):
            current_match_val = 0
            name = song.song_name
            for word in name.split(" "):
                for s in song_str.split(" "):
                    if word.lower()==s.lower():
                        current_match_val += 1
            if current_match_val > max_match_val:
                max_match_ind = ind
        if self.Songs[max_match_ind].song_name in self.display_songs.get(0,"end"):
            print("song name ",self.Songs[max_match_ind].song_name)
            self.display_songs.delete(self.display_songs.get(0,"end").index(self.Songs[max_match_ind].song_name))
        self.display_songs.insert(0, self.create_song_name(self.Songs[max_match_ind]))
        
                     
    def search_song_spotify(self):
        """search song in spotify, check if locally available"""
        song = self.search_field.get()
        
        ans = self.search_cls.from_search_term(query=song)
        
        if not ans.file_path and not ans.song_name: 
            raise ValueError("Could not find song")
        
        self.Song = ans
        self.Songs.append(ans)
        
        #show results
        if ans.song_name in list(self.display_songs.keys()):
            # already downloaded
            self.display_songs.delete(self.display_songs.get(0,"end").index(ans.song_name))
            
        # insert as first element
        self.display_songs.insert(0, ans.song_name)

    def create_song_name(self,song:Song)->str:
        return f"{song.song_name} - {song.contributing_artists[0]}"
    
    def get_song_name_from_repr(self, repr:str)->str:
        return repr.split("-")[0].strip()
    
    def show_songs(self,songs:list[Song]):
        """create a listbox for songs """
        if not songs:
            songs = []
        # code for creating table
        self.display_songs = Listbox(self.root, width=80, fg='blue',
                            font=('Arial',16,'bold'))
        self.display_songs.bind('<<ListboxSelect>>',self.select_song_by_cursor)
        
        for ind, song in enumerate(songs):
            
            self.display_songs.grid(column = 0,row=1+ind)
            self.display_songs.insert(END, self.create_song_name(song))
            

def main(search,downloader,lyrics,vocal_remover):
    root = Tk()
    Interface(root,search,downloader,lyrics,vocal_remover)
    root.mainloop()
