import os
import pickle
from tkinter import Button, Label, Frame,Entry,StringVar,Toplevel,END,Listbox,Tk, Scrollbar,N,S,W,E,SINGLE,VERTICAL
from .music_player import MusicPlayer
from .lyrics_window import show_lyrics
from backend import Search, Downloader, VocalRemover, SongLyrics
from utils import Song
from pathlib import Path
from backend import DownloadedSongs
  
class Interface(Tk):
    def __init__(self, config):
        super().__init__()
        self.downloads_path = Path(config["downloads_path"])
        self.export_folder = Path(config["export_folder"])
        #make directory if it does not exist
        self.downloads_path.parent.mkdir(parents=True, exist_ok=True)
        self.search_cls = Search(config)
        self.download_cls = Downloader(config)
        self.lyrics_cls = SongLyrics()
        self.vocal_remover = VocalRemover(config)
        self.file_search = DownloadedSongs(config["downloads_path"])
        self.root_height = int(config["window_height"])
        self.root_width = int(config["window_width"])
        print(f"root gets size {self.root_height}x{self.root_width}")
        self.title("Select a Song")
        self.geometry(f"{self.root_width}x{self.root_height}+722+310")
        self.configure(bg='light grey')
        
        self.make_search_interface()
        
        self.Songs = self.load_songs_from_file()
        self.show_songs(self.Songs)
        self.music_player = None
        self.Song = None
        self.display_sons = None
        self.use_complete_song = False
    
    def make_search_interface(self):
        searchinterface_height=int(self.root_height/30)
        searchinterface_width = int(self.root_width/8)
        searchinterface = Frame(self,height=searchinterface_height, width=searchinterface_width)
        print(f"searchengine size: {searchinterface_height}x{searchinterface_width}")
        #search buttons
        self.search_spot_commit = Button(searchinterface,
                                         text="Search on Spotify",
                                         width=int(searchinterface_width/4),
                                         height=int(searchinterface_height/4),
                                         fg = 'black',
                                         font=('Arial',16,'bold'),
                                         background='blue',
                                         activeforeground='green',
                                         borderwidth="2",
                                         relief="groove",
                                         command=self.search_song_spotify)
        self.search_loc_commit = Button(searchinterface,
                                        text = "Search Local",
                                        height=int(searchinterface_height/4),
                                        width=int(searchinterface_width/4),
                                        fg = 'black',font=('Arial',16,'bold'),
                                        background = 'blue',
                                        activeforeground='green',
                                        borderwidth="2", 
                                        relief="groove",
                                        command=self.search_song_local)

        self.search_spot_commit.grid(column=1,row=0,sticky=W+E)
        self.search_loc_commit.grid(column=1,row=1,sticky=W+E)
        
        #input field
        label = Label(searchinterface,
                      text = "Enter your search term: ",
                      font=('Arial',16,'bold'),
                      height=int(searchinterface_height/4),
                      width=int(searchinterface_width/2))
        label.grid(column=0,row=0,sticky=W+E)
        
        text = StringVar()
        self.search_field = Entry(searchinterface,
                                  font=('Arial',16,'bold'), 
                                  width=int(searchinterface_width/2),
                                  textvariable=text, 
                                  borderwidth="2", 
                                  relief="groove")
        self.search_field.grid(column=0,row=1,sticky=W+N)
        
        searchinterface.grid(column=0,row=0,sticky=N+E+W,padx=1,pady=1)
    
    def load_songs_from_file(self) -> list[Song]:
        """load the saved song objects from file"""
        print("searching in ", self.downloads_path)
        if not self.downloads_path.is_file():
            #make file if it does not exist
            print("make downloads file because it does not exist")
            open(self.downloads_path,"wb+").close()
        #make sure file is not empty, this causes error when pickling
        try:
            if os.path.getsize(self.downloads_path) > 0:     
                with open(self.downloads_path,"rb") as f:
                    songs = pickle.load(f)
                    return songs
            print("empty file")
            return []
        except ModuleNotFoundError:
            print("deleting downloadsfile because pickling failed file")
            #self.downloads_path.unlink()
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
            if song.display_name == name:
                match_song = song
                break
        
        if match_song is None:
            print("no match found")
            return
        
        #set self.Song to the currently selected song
        self.Song = match_song
        path = str(self.Song.file_path)
        if path == []:
            #self.display_songs.itemconfig(index, {'activeforeground':'red'})
            raise ValueError(f"stored no path for this song: {name}")
        
        saved_at = self.download_song()
        # check is filepath for audio file exists
        if not os.path.isfile(path) or not os.path.isfile(path.replace(".mp3",".wav")):
            #download song if it does not exist
            self.display_songs.itemconfig(index, {'acitveforeground':'green'})
            
            assert saved_at == path
            
        basename = os.path.splitext(os.path.basename(path))[0]
        file = f"{self.export_folder}/backing_tracks/{basename}_Instruments.wav"
        # make sure karaoke version of song exists, else create
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
        #self.display_songs.itemconfig(index, {'activeforeground':'black'})
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
            self.play_complete_song.configure(foreground="red") 
        else:
            self.play_complete_song.config(relief="sunken")
            self.use_complete_song = True
            self.play_complete_song.configure(foreground="green") 

    def search_song_local(self):
        """local search in case no internet is available"""
        song_str = self.search_field.get()
        max_match_ind = -1
        max_match_val = 0
        
        if self.Songs == [] or self.Songs is None:
            print("no songs found")
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
        if song == "" or song is None:
            print("No input...") 
            return
        
        ans = self.search_cls.from_search_term(query=song)
        if ans is None:
            print("No answer from search")
            return
        if isinstance(ans,Path):
            self.Song = self.file_search.song_from_path(ans)
            if self.Song is not None:
                # add song to file
                self.file_search.handle_download_success(self.Song)
            else: return
            
        else: self.Song = ans
        
        
        print("current song: ", self.Song.song_name)
        if self.Song is None:
            print("song object not created")
            return
            
        self.Songs.append(self.Song)
        
        #show results
        if self.Song.song_name in list(self.display_songs.keys()):
            # already downloaded
            self.display_songs.delete(self.display_songs.get(0,"end").index(self.Song.display_name))
        # insert as first element
        self.display_songs.insert(0, self.Song.display_name)


    def show_songs(self,songs:list[Song]):
        """create a listbox for songs """
        if not songs:
            songs = []
        
        palette_height = int(self.root_height/30)
        palette_width = int(self.root_width/8)
        song_palette = Frame(self,background='grey',height=palette_height, width=palette_width)
        
        # code for creating table where songs will be shown
        self.display_songs = Listbox(song_palette, 
                                     width=int(palette_width/2), 
                                     height=palette_height, 
                                     fg='blue',
                                     font=('Arial',16,'bold'),
                                     selectmode=SINGLE,
                                     borderwidth="2", 
                                     relief="groove")
        
        self.display_songs.bind('<<ListboxSelect>>',self.select_song_by_cursor)
        self.display_songs.grid(column=0,row=0,sticky=N+S)
        
        #add a scrollbar
        scrollbar = Scrollbar(song_palette, 
                              orient=VERTICAL,
                              command=self.display_songs.yview,
                              bg='black',
                              width=10,
                              borderwidth="2",
                              relief="groove",
                              activebackground='green')
        scrollbar.grid(sticky=N+S,column=1,row=0)
        
        self.display_songs.config(yscrollcommand=scrollbar.set)
        for song in songs:
            self.display_songs.insert(END, song.display_name) 
            
        self.play_complete_song = Button(song_palette,
                                        text = 'Play song with vocals',
                                        fg = 'black',
                                        width=int(palette_width/5)-2,
                                        height=int(palette_height/30),
                                        font=('Arial',16,'bold'), 
                                        foreground='grey',
                                        activeforeground='yellow',
                                        borderwidth='2', 
                                        relief='groove',
                                        command=self.add_song_to_playlist)
        self.play_complete_song.grid(column=2, row=0,sticky=N+E)

        song_palette.grid(column=0,row=1,sticky=N+S+E+W, padx=1,pady=1,ipadx=5,ipady=5)
            

def run_gui(config):
    
    root = Interface(config)
    root.mainloop()
