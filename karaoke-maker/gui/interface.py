import os
import pickle
from tkinter import Button,Entry,StringVar,Toplevel,END,Listbox,Tk, Scrollbar,N,S,W,E,SINGLE,VERTICAL
from gui import MusicPlayer, show_lyrics
from backend import Search,Downloader, VocalRemover, SongLyrics, Song
from pathlib import Path
  
class Interface(Tk):
    def __init__(self, config):
        super().__init__()
        self.downloads_path = Path(config["downloads_path"])
        #make directory if it does not exist
        self.downloads_path.parent.mkdir(parents=True, exist_ok=True)
        self.search_cls = Search(config)
        self.download_cls = Downloader(config)
        self.lyrics_cls = SongLyrics()
        self.vocal_remover = VocalRemover(config)
        
        self.title("Select a Song")
        self.geometry("1000x600+722+310")
        self.configure(bg='light grey')
        
        self.search_spot_commit = Button(self,text = "Search on Spotify",width=30,fg = 'black',font=('Arial',16,'bold'),activebackground='#00ff00',command=self.search_song_spotify)
        self.search_loc_commit = Button(self,text = "Search Local",width=30,fg = 'black',font=('Arial',16,'bold'),activebackground='#00ff00',command=self.search_song_local)
        self.play_complete_song = Button(self,text = "Play song with vocals",width=30,fg = 'black',font=('Arial',16,'bold'),activebackground='green',command=self.add_song_to_playlist)
        self.search_spot_commit.grid(column=1,row=0)
        self.search_loc_commit.grid(column=1,row=1)
        self.play_complete_song.grid(column = 1, row=2,sticky="n")
        
        text = StringVar()
        self.search_field = Entry(self,width=80,textvariable=text)
        self.search_field.grid(column=0,row=0)
        self.Songs = self.load_songs_from_file()
        self.show_songs(self.Songs)
        self.music_player = None
        self.Song = None
        self.display_sons = None
        self.use_complete_song = False
        
    def load_songs_from_file(self) -> list[Song]:
        """load the saved song objects from file"""
        
        if not self.downloads_path.is_file():
            #make file if it does not exist
            open(self.downloads_path,"wb+").close()
        #make sure file is not empty, this causes error when pickling
        try:
            if os.path.getsize(self.downloads_path) > 0:     
                with open(self.downloads_path,"rb") as f:
                    songs = pickle.load(f)
                    return songs
            return []
        except ModuleNotFoundError:
            self.downloads_path.unlink()
            return []

            
    def select_song_by_cursor(self,event):
        """select a song by cursor"""
        index = self.display_songs.curselection()
        
        if isinstance(index,tuple) and index != ():
            index = index[0]
        else: return
        #color the selected element
        self.display_songs.itemconfig(index, {'bg':'green'})
        name = self.display_songs.get(index)
        
        #find a match in all songs
        match_song = None
        for song in self.Songs:
            if song.display_name == name or song.song_name == name:
                match_song = song
                break
        # no match means error happened
        if not match_song:
            raise ValueError("no match found")
        
        #set self.Song to the currently selected song
        self.Song = match_song
        path = str(self.Song.file_path)
        if path == []:
            self.display_songs.itemconfig(index, {'bg':'red'})
            raise ValueError(f"stored no path for this song: {name}")
        
        if not os.path.isfile(path) or not os.path.isfile(path.replace(".mp3",".wav")):
            print("no file named: ",path )
            #download song if it does not exist
            self.display_songs.itemconfig(index, {'bg':'yellow'})
            saved_at = self.download_song()
            assert saved_at == path
            
        basename = os.path.splitext(os.path.basename(path))[0]
        file = f"karaoke-maker/data/backing_tracks/{basename}_Instruments.wav"
        if not os.path.isfile(file):
            # extract vocals from downloaded song
            self.display_songs.itemconfig(index, {'bg':'orange'})
            self.vocal_remover.remove_vocals(path)
        # play song if its instrumental can be found
        if not self.music_player:
            self.music_player = MusicPlayer(self)
        if self.use_complete_song:
            file = path    
        self.music_player.append_song(file)
        self.display_songs.itemconfig(index, {'bg':'white'})
        if self.Song.lyrics != None:
            show_lyrics(self.Song.lyrics,Toplevel(self))
        
        
    def download_song(self):
        """downloads song if it is not in file"""
        if self.Song is not None:
            saving_name = self.download_cls.download_song(self.Song)
            return saving_name
        
    def add_song_to_playlist(self):
        if self.play_complete_song.config('relief')[-1] == 'sunken':
            self.play_complete_song.config(relief="raised")
            self.use_complete_song = False
            self.play_complete_song.configure(bg="red") 
        else:
            self.play_complete_song.config(relief="sunken")
            self.use_complete_song = True
            self.play_complete_song.configure(bg="green") 

    def search_song_local(self):
        song_str = self.search_field.get()
        max_match_ind = -1
        max_match_val = 0
        
        if self.Songs == [] or self.Songs is None:
            return
        
        for ind,song in enumerate(self.Songs):
            current_match_val = 0
            name = song.song_name
            for word in name.split(" "):
                for s in song_str.split(" "):
                    if word.lower()==s.lower():
                        current_match_val += 1
            if current_match_val > max_match_val:
                max_match_ind = ind
        if max_match_ind != -1:
            song_name = self.Songs[max_match_ind].display_name
            if song_name in self.display_songs.get(0,"end"):
                self.display_songs.delete(self.display_songs.get(0,"end").index(song_name))
            self.display_songs.insert(0, song_name)
        
                     
    def search_song_spotify(self):
        """search song in spotify, check if locally available"""
        song = self.search_field.get()
        ans = self.search_cls.from_search_term(query=song)
        if not ans:
            return ValueError("Could not find song")
        if not ans.file_path and not ans.song_name: 
            raise ValueError("Could not find song path or name")
        self.Song = ans
        if not self.Songs:
            self.Songs = []
        self.Songs.append(ans)
        
        #show results
        if ans.song_name in list(self.display_songs.keys()):
            # already downloaded
            self.display_songs.delete(self.display_songs.get(0,"end").index(ans.song_name))
        # insert as first element
        self.display_songs.insert(0, ans.song_name)

    # def create_song_name(self,song:Song)->str:
    #     return f"{song.song_name} - {song.contributing_artists[0]}"
    
    def get_song_name_from_repr(self, repr:str)->str:
        return repr.split("-")[0].strip()
    
    def show_songs(self,songs:list[Song]):
        """create a listbox for songs """
        if not songs:
            songs = []
        
        # code for creating table
        self.display_songs = Listbox(self, width=80, height=80, fg='blue',
                            font=('Arial',16,'bold'),selectmode=SINGLE)
        self.display_songs.bind('<<ListboxSelect>>',self.select_song_by_cursor)
        scrollbar = Scrollbar(self, orient=VERTICAL,command=self.display_songs.yview)
        scrollbar.grid(sticky=S+E,column=3,row=3)
        self.display_songs.config(yscrollcommand=scrollbar.set)
        
        
        #if songs == []:
        self.display_songs.grid(column = 0,row=3,sticky=N+S+W+E)
            
        for ind, song in enumerate(songs):
            #self.display_songs.grid(column = 0,row=1+ind)
            self.display_songs.insert(END, song.display_name)
            

def run_gui(config):
    
    root = Interface(config)
    root.mainloop()
