import os
import pickle
import tkinter as tk
from tkinter.messagebox import showerror, showinfo
from tkinter import ttk
from .music_player import MusicPlayer
from .lyrics_window import LyricsWindow
from backend import Search, Downloader, VocalRemover, SongLyrics
from utils import Song
from pathlib import Path
from backend import DownloadedSongs
  
class Interface(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.downloads_path = Path(config["downloads_path"])
        self.export_folder = Path(config["export_folder"])
        #make directory if it does not exist
        if not self.downloads_path.exists():
            self.downloads_path.parent.mkdir(parents=True, exist_ok=True)
            
        self.search_cls = Search(config)
        self.download_cls = Downloader(config)
        self.lyrics_cls = SongLyrics()
        self.vocal_remover = VocalRemover(config)
        self.file_search = DownloadedSongs(config["downloads_path"])
        
        #configure window size
        self.root_height = int(config["root_height"])
        self.root_width = int(config["root_width"])

        self.title("KaraokeMaker")
        self.geometry(f"{self.root_width}x{self.root_height}+0+0")
        self.state = False
        self.attributes("-fullscreen",False)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.end_fullscreen)
        
        self.configure(bg='light grey')
        self.resizable(True, True)
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)#
        self.style = ttk.Style()
        #self.style.configure()
        
        self.make_search_interface()
        self.make_music_player()
        self.make_lyrics_window()
        
        # initialize necessairy variables
        self.Songs = self.load_songs_from_file()
        self.show_songs(self.Songs)
        self.Song = None
        self.display_sons = None
        self.use_complete_song = False
        
    def make_music_player(self):
        self.music_player = MusicPlayer(self)
        self.music_player.grid(column=0,row=2,sticky=tk.NSEW)
        #configure frame
        self.music_player.grid_columnconfigure(index=0,weight=1,minsize=200)
        self.music_player.grid_rowconfigure(index=0,weight=1,minsize=100)
        
        
    def make_lyrics_window(self):
        self.lyrics_window = LyricsWindow(self)
        self.lyrics_window.grid(rowspan=3, row=0, column=1, sticky=tk.NSEW)
        #configure frame
        self.lyrics_window.grid_columnconfigure(index=1,weight=1,minsize=200)
        self.lyrics_window.grid_rowconfigure(index=0,weight=1,minsize=150)
        self.lyrics_window.grid_rowconfigure(index=1,weight=1,minsize=150)
        self.lyrics_window.grid_rowconfigure(index=2,weight=1,minsize=150)

        
    def set_lyrics(self,text:str):
        self.lyrics_window.set_lyrics(text)
        
    def make_search_interface(self):
        """create the interface for searching song"""
        
        searchinterface = ttk.Frame(self,padding=10)
        
        # create search buttons
        self.search_spot_commit = ttk.Button(searchinterface,
                                         text="Search on Spotify",
                                         command=self.search_song_spotify,
                                         width=20)
        
        self.search_loc_commit = ttk.Button(searchinterface,
                                        text = "Search Local",
                                        command=self.search_song_local,
                                        width=20)

        self.search_spot_commit.grid(column=1,row=1,sticky=tk.EW)
        self.search_loc_commit.grid(column=1,row=2,sticky=tk.EW)
        
        #input field
        label = ttk.Label(searchinterface,
                      text = "Enter your search term: ",
                      font=('Arial',16,'bold'))
        label.grid(column=0,row=0,sticky=tk.NSEW)
        
        text = tk.StringVar()
        self.search_field = ttk.Entry(searchinterface,
                                      width=70,
                                  font=('Arial',16,'bold'), 
                                  textvariable=text)
        self.search_field.grid(column=0,row=1,sticky=tk.NSEW)
        
        searchinterface.grid(column=0,row=0,sticky=tk.NSEW)
        #configure frame
        searchinterface.grid_columnconfigure(index=0,weight=1,minsize=30)
        searchinterface.grid_rowconfigure(index=1,weight=1,minsize=10)
    
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
            print("TODO: deleting downloadsfile because pickling failed file")
            #self.downloads_path.unlink()
            showerror("File where downloads should be listed was not found")
            return []

            
    def select_song_by_cursor(self):
        """select a song by cursor"""
        #index = self.display_songs.curselection()
        current_item = self.display_songs.focus()
        name,artist = self.display_songs.item(current_item)["values"]
        
        #find a match in all songs
        for song in self.Songs:
            if song.song_name == name:
                if song.contributing_artists[0]==artist:
                    self.Song = song
                    break
        
        if self.Song is None:
            showerror("Song is not in downloadsfile")
            return
        
        path = str(self.Song.file_path)
        if path == []:
            #self.display_songs.itemconfig(index, {'activeforeground':'red'})
            showerror(f"stored no path for this song: {name}")
            return        
        
        saved_at = self.download_song()
        # check is filepath for audio file exists
        #download song if it does not exist
        #self.display_songs.itemconfig(index, {'acitveforeground':'green'})
           
            
        basename = os.path.splitext(os.path.basename(path))[0]
        file = f"{self.export_folder}/backing_tracks/{basename}_Instruments.wav"
        # make sure karaoke version of song exists, else create
        if not os.path.isfile(file):
            # extract vocals from downloaded song
            #self.display_songs.itemconfig(index, {'bg':'orange'})
            self.vocal_remover.remove_vocals(path)
            
        # play song if its instrumental can be found
        if self.use_complete_song:
            file = path    
        
        self.music_player.append_song(file)
        #self.display_songs.itemconfig(index, {'activeforeground':'black'})
        if self.Song.lyrics != None:
            self.set_lyrics(self.Song.lyrics)
        
        
    def download_song(self):
        """downloads song if it is not in file"""
        if self.Song is not None:
            saving_name = self.download_cls.download_song(self.Song)
            return saving_name
        
    def add_song_to_playlist(self):
        if self.play_complete_song.config('relief')[-1] == 'sunken':
            #self.play_complete_song.config(relief="raised")
            self.use_complete_song = False
            #self.play_complete_song.configure(foreground="red") 
        else:
            #self.play_complete_song.config(relief="sunken")
            self.use_complete_song = True
            #self.play_complete_song.configure(foreground="green") 

    def search_song_local(self):
        """local search in case no internet is available"""
        
        
        song_str = self.search_field.get()
        max_match_ind = -1
        max_match_val = 0
        
        if self.Songs == [] or self.Songs is None:
            showinfo("no songs found locally")
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
            current_item = self.display_songs.focus(self.Songs[max_match_ind].display_name)
            self.display_songs.move(current_item,"",0)
            
        else: 
            showerror("song not available locally")
        
                     
    def search_song_spotify(self):
        """search song in spotify, check if locally available"""
        song = self.search_field.get()
        if song == "" or song is None:
            showinfo("can't search for nothing...")
            return
        ans = self.search_cls.from_search_term(query=song)
        print("spotify returned: ",type(ans))
        if ans is None:
            showerror("No answer from search on spotify, retry!")
            return
        if isinstance(ans,Path):
            self.Song = self.file_search.song_from_path(ans)
            if self.Song is not None:
                # add song to file
                self.file_search.handle_download_success(self.Song)
            else: return
        else: self.Song = ans
        if self.Song is None:
            showerror("song object could not created")
            return
            
        self.Songs.append(self.Song)
        #show results
        current_item=self.display_songs.item(self.Song.song_name)
        print("selected :",type(current_item),current_item)
        #move to first index
        current_item = self.display_songs.focus(self.Song.display_name)
        self.display_songs.move(current_item, '',0)
        

    def show_songs(self,songs:list[Song]):
        """create a listbox for songs """
        if not songs:
            songs = []
        
        song_palette = ttk.Frame(self,padding=10)
        
        
        # code for creating table where songs will be shown
        columns=("song_name","artist")
        self.display_songs = ttk.Treeview(song_palette, columns=columns, show='headings'
                                     )
        self.display_songs.heading('song_name', text='Song Name')
        self.display_songs.heading('artist', text='Arist Name')
        
        self.display_songs.grid(rowspan=3,column=0,sticky=tk.NSEW)
        
        for song in songs:
            self.display_songs.insert('',
                                      tk.END, 
                                      iid=song.display_name, 
                                      values=(song.song_name,song.contributing_artists[0])) 
            
        
        # add a scrollbar
        scrollbar = ttk.Scrollbar(song_palette, orient=tk.VERTICAL, command=self.display_songs.yview)
        self.display_songs["yscrollcommand"]=scrollbar.set
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        #button for selecting a song
        self.play_complete_song = ttk.Button(song_palette,
                                        text = 'Play Selected Song',
                                        command=self.select_song_by_cursor,
                                        width=20)
        self.play_complete_song.grid(column=2, row=0,sticky=tk.N)
        
        #button for playing complete song (with vocals)
        self.play_complete_song = ttk.Button(song_palette,
                                        text = 'Play song with vocals',
                                        command=self.add_song_to_playlist,
                                        width=20)
        self.play_complete_song.grid(column=2, row=1,sticky=tk.N)
        
        # set songs in the second row of the first column of root window
        song_palette.grid(column=0,row=1,sticky=tk.NSEW)
        
        # let only the box with songs grow when resized
        song_palette.grid_columnconfigure(index=0,weight=1,minsize=20)
        song_palette.grid_rowconfigure(index=2,weight=1,minsize=10)
        
    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.attributes("-fullscreen", False)
        return "break"
            

def run_gui(config):
    
    root = Interface(config)
    root.mainloop()
