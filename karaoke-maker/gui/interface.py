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
        self.config=config
        self.downloads_path = Path(config["downloads_path"])
        self.export_folder = Path(config["export_folder"])
        #make directory if it does not exist
        if not self.downloads_path.exists():
            self.downloads_path.parent.mkdir(parents=True, exist_ok=True)
            
        self.search_cls = Search(config)
        self.lyrics_cls = SongLyrics()
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
        self.grid_rowconfigure(2,weight=0)#
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
        self.thread_running = False
        
    def make_music_player(self):
        self.music_player = MusicPlayer(self)
        self.music_player.grid(column=0,row=2,sticky=tk.NSEW)
        #configure frame
        self.music_player.grid_columnconfigure(index=0,weight=1,minsize=200)
        self.music_player.grid_rowconfigure(index=2,weight=1,minsize=30)
        
        
    def make_lyrics_window(self):
        self.lyrics_window = LyricsWindow(self)
        self.lyrics_window.grid(rowspan=3, row=0, column=1, sticky=tk.NSEW)
        #configure frame
        self.lyrics_window.grid_columnconfigure(index=0,weight=1,minsize=550)
        self.lyrics_window.grid_columnconfigure(index=1,weight=1,minsize=10)
        self.lyrics_window.grid_rowconfigure(index=0,weight=1,minsize=30)
        self.lyrics_window.grid_rowconfigure(index=1,weight=1,minsize=30)
        self.lyrics_window.grid_rowconfigure(index=2,weight=1,minsize=30)

        
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
                                  font=('Arial',16), 
                                  textvariable=text)
        self.search_field.grid(column=0,row=1,sticky=tk.NSEW)
        
        searchinterface.grid(column=0,row=0,sticky=tk.NSEW)
        #configure frame
        searchinterface.grid_columnconfigure(index=0,weight=1,minsize=30)
        searchinterface.grid_rowconfigure(index=1,weight=1,minsize=10)
    
    def load_songs_from_file(self) -> list[Song]:
        """load the saved song objects from file"""
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
            return []
        except ModuleNotFoundError:
            print("TODO: deleting downloadsfile because pickling failed file")
            #self.downloads_path.unlink()
            showerror("Error","Downloadsfile was not found")
            return []

            
    def select_song_by_cursor(self):
        """select a song by cursor"""
        if self.thread_running == True:
            print("thread running.... wait")
            return
        current_item = self.display_songs.focus()
        if len(self.display_songs.item(current_item)["values"]) == 2:
            name,artist = self.display_songs.item(current_item)["values"]
        else: 
            showinfo("Song not found","song not available, please delete!")
            return
        #find a match in all songs
        for song in self.Songs:
            if song.song_name == name:
                if song.contributing_artists[0]==artist:
                    self.Song = song
                    break
        
        if self.Song is None:
            showerror("Downloads","Song not in downloadsfile")
            return
        
        path = str(self.Song.file_path)
        if path == []:
            showerror("Path Error", "no path for this song")
            return        
        
            
        basename = os.path.splitext(os.path.basename(path))[0]
        file = f"{self.export_folder}/backing_tracks/{basename}_Instruments.wav"
        
        #download song if it does not exist
        if not self.Song.file_path.is_file():
            self.download_song()
            
        # make sure karaoke version of song exists, else create
        if not os.path.isfile(file):
            self.remove_voc(path)
           
        # play song if its instrumental can be found
        if self.play_complete_song['state']==tk.ACTIVE:
            file = path    
        
        self.music_player.append_song(file)
        if self.Song.lyrics != None:
            self.set_lyrics(self.Song.lyrics)
   

    def remove_voc(self,path):
        """remove vocals in a seperate thread"""
        if not self.thread_running and Path(path).is_file():
            vocalremover_thread = VocalRemover(file=path,config=self.config)
            vocalremover_thread.start() 
            self.monitor(vocalremover_thread)       
        else:
            self.after(1500, self.remove_voc, path)
        
        
    def download_song(self):
        """downloads song if it is not in file"""
        if self.Song is not None:
            if not self.thread_running:
                downloading_thread = Downloader(song_obj=self.Song,config = self.config)
                downloading_thread.start()
                self.monitor(downloading_thread)
            else:
                print("delaying download")
                self.after(1500, self.download_song)
            
    def monitor(self,thread):
        if thread.is_alive():
            self.thread_running = True
            # check the thread every 200ms
            self.after(200, lambda: self.monitor(thread))
        else:
            self.thread_running = False
            print(f"thread ended {thread.name}")
        
        
    def toggle_complete_song(self):
        if self.play_complete_song['state'] == tk.DISABLED:
            self.play_complete_song['state'] = tk.ACTIVE
        else:
            self.play_complete_song['state'] = tk.DISABLED
    
    def delete_song(self):
        current_item = self.display_songs.focus()
        if len(self.display_songs.item(current_item)["values"]) == 2:
            name,artist = self.display_songs.item(current_item)["values"]
        else: 
            showinfo("Song-Info","This song is not available, please delete!")
            return
        #find a match in all songs
        for song in self.Songs:
            if song.song_name == name:
                if song.contributing_artists[0]==artist:
                    self.Song = song
                    break
        
        if self.Song:
            self.Songs.remove(self.Song)
            self.file_search.remove_song_from_file(self.Song)
            self.display_songs.delete(current_item)
            
            

    def search_song_local(self):
        """local search in case no internet is available"""
        if self.thread_running == True:
            print("thread running.... wait")
            return
        
        song_str = self.search_field.get()
        max_match_ind = -1
        max_match_val = 0
        
        if self.Songs == [] or self.Songs is None:
            showinfo("Song-Info","no songs found in downloadsfile")
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
            showerror("song not available")
        
                     
    def search_song_spotify(self):
        """search song in spotify, check if locally available"""
        
        if self.thread_running == True:
            print("thread running.... wait")
            return
        
        song = self.search_field.get()
        
        if song == "" or song is None:
            showinfo("empty search")
            return
        try:
            ans = self.search_cls.from_search_term(query=song)
        except Exception as e:
            showerror(str(e))
            return
        
        if isinstance(ans,Path):
            self.Song = self.file_search.song_from_path(ans)
            if self.Song is not None:
                # add song to file
                print("handling download succes with song: ", self.Song.file_path)
                self.file_search.handle_download_success(self.Song)
            else: 
                return
            
        else: self.Song = ans
        if self.Song is None:
            showerror("song object not created")
            return
        
        if self.Song in self.Songs:
            #show results
            current_item=self.display_songs.item(self.Song.song_name)
            #move to first index
            current_item = self.display_songs.focus(self.Song.display_name)
            self.display_songs.move(current_item, '',0)
        else:
            self.Songs.append(self.Song)
            self.display_songs.insert('',
                                      0, 
                                      iid=self.Song.display_name, 
                                      values=(self.Song.song_name,self.Song.contributing_artists[0])) 
            
        

    def show_songs(self,songs:list[Song]):
        """create a listbox for songs """
        if not songs:
            songs = []
        
        song_palette = ttk.Frame(self,padding=3)
        
        
        # code for creating table where songs will be shown
        columns=("song_name","artist")
        self.display_songs = ttk.Treeview(song_palette, columns=columns, show='headings'
                                     )
        self.display_songs.heading('song_name', text='Song Name')
        self.display_songs.heading('artist', text='Arist Name')
        
        self.display_songs.grid(rowspan=3,column=0,sticky=tk.NSEW)
        
        for song in songs:
            try:
                self.display_songs.insert('',
                                      tk.END, 
                                      iid=song.display_name, 
                                      values=(song.song_name,song.contributing_artists[0])) 
            except Exception as e:
                print("song not available: ", e)
                continue
            
        
        # add a scrollbar
        scrollbar = ttk.Scrollbar(song_palette, orient=tk.VERTICAL, command=self.display_songs.yview)
        self.display_songs["yscrollcommand"]=scrollbar.set
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        #button for selecting a song
        self.select_song = ttk.Button(song_palette,
                                        text = 'Load selected Song',
                                        command=self.select_song_by_cursor,
                                        width=20)
        self.select_song.grid(column=2, row=0,sticky=tk.N)
        
        #button for playing complete song (with vocals)
        self.play_complete_song = ttk.Button(song_palette,
                                        text = 'Play song with vocals',
                                        command=self.toggle_complete_song,
                                        width=20,default=tk.DISABLED)
        self.play_complete_song.grid(column=2, row=1,sticky=tk.N)
        
        self.delete_songs = ttk.Button(song_palette,
                                        text = 'Delete song',
                                        command=self.delete_song,
                                        width=20,default=tk.DISABLED)
        self.delete_songs.grid(column=2, row=2, sticky=tk.N)
        
        
        # set songs in the second row of the first column of root window
        song_palette.grid(column=0,row=1,sticky=tk.NSEW)
        
        # let only the box with songs grow when resized
        song_palette.grid_columnconfigure(index=0,weight=1,minsize=30)
        song_palette.grid_rowconfigure(index=0,weight=0,minsize=10)
        song_palette.grid_rowconfigure(index=1,weight=0,minsize=10)
        song_palette.grid_rowconfigure(index=2,weight=1,minsize=15)
        
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
