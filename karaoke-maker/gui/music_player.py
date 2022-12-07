from pathlib import Path
import time
import tkinter as tk 
from tkinter import ttk
import pygame

PAUSED = "PAUSED"
PLAYING = "PLAYING"
STOPPED = "STOPPED"


class MusicPlayer(ttk.Frame):
    
    def __init__(self,root):
        super().__init__(root)
        pygame.init()
        pygame.mixer.init()
        self.track = tk.StringVar()
        self.status = tk.StringVar()
        self.status.set(STOPPED)
        self.resizable=(True,True)
        self.songs: list[str] = list()
        #Frame for running track
        trackframe = ttk.Frame(self,relief=tk.GROOVE)
        trackframe.place(x=0,y=0,width=500,height=40)
        trackframe.pack(side=tk.RIGHT,fill=tk.BOTH,expand=1,padx=2,pady=2)
        ttk.Label(trackframe,
                  textvariable=self.track,
                  width=40,
                  font=("Arial",14)).grid(row=0,column=0,columnspan=3,padx=5,pady=5)

        ttk.Label(trackframe,
                  textvariable=self.status,
                  font=("Arial",12)).grid(row=1,column=0,columnspan=3,padx=5,pady=5,sticky=tk.NE)
        self.progressbar = ttk.Progressbar(trackframe,
                                           length=300,
                                           maximum=100,
                                           orient="horizontal",
                                           mode="determinate")
        self.progressbar.grid(column = 0,row=2,columnspan=3,padx=10,pady=10)

        #frame for buttons
        buttonframe = ttk.Frame(self,relief=tk.GROOVE)
        buttonframe.place(x=0,y=100,width=500,height=30)
        buttonframe.pack(side=tk.TOP,fill=tk.X,expand=1,padx=2,pady=2)
        ttk.Button(buttonframe,
                   text="PLAYSONG",
                   command=self.playsong,
                   width=10).grid(row=0,column=0,padx=2,pady=2)

        ttk.Button(buttonframe,
                   text="STOPSONG",
                   command=self.stopsong,
                   width=10).grid(row=0,column=1,padx=2,pady=2)
        ttk.Button(buttonframe,
                   text="NEXT SONG",
                   command=self.nextsong,
                   width=10).grid(row=0,column=2,padx=2,pady=2)
        
        #frame for Playlist
        songsframe = ttk.Frame(self,relief=tk.GROOVE)
        songsframe.place(x=400,y=0,width=300,height=40)
        songsframe.pack(side=tk.LEFT,fill=tk.BOTH,expand=1,padx=2,pady=2)
        scrol_y = tk.Scrollbar(songsframe,orient=tk.VERTICAL,relief=tk.GROOVE)
        scrol_x = tk.Scrollbar(songsframe,orient=tk.HORIZONTAL,relief=tk.GROOVE)
        self.playlist = tk.Listbox(songsframe,
                                   yscrollcommand=scrol_y.set,
                                   xscrollcommand=scrol_y.set,
                                   selectbackground="gold",
                                   selectmode=tk.SINGLE,
                                   font=("Arial",12),
                                   bg="white",
                                   fg="blue",
                                   bd=5,
                                   relief=tk.GROOVE)
        scrol_y.pack(side=tk.RIGHT,fill=tk.BOTH)
        scrol_y.config(command=self.playlist.yview)
        scrol_x.pack(side=tk.BOTTOM,fill=tk.BOTH)
        scrol_x.config(command=self.playlist.xview)
        self.playlist.pack(fill=tk.BOTH,side=tk.RIGHT,expand=1,padx=2,pady=2)
        
        self.grid_columnconfigure(index=0,weight=1,minsize=100)
        self.grid_columnconfigure(index=1,weight=1,minsize=100)
        
    
    def nextsong(self):
        """loads next song in playlist"""
        
        
        active = self.playlist.get(tk.ACTIVE)
        if active is None:
            self.stopsong()
            
        current_song_index = self.playlist.get(0,tk.END).index(active)
        del self.songs[current_song_index]
        self.playlist.delete(current_song_index)
        self.playlist.activate(current_song_index-1)
        
        if self.playlist.get(current_song_index-1) is None:
            print("next element is None")
            self.stopsong()
            self.playlist.delete(current_song_index)
        else: 
            self.playsong()
        
    def append_song(self,track:str):
        """adds a song to the playlist and to pathnames(self.songs)"""
        self.songs.append(track)
        self.playlist.insert(tk.END,self.song_name_from_path(track))

    def song_name_from_path(self,path:str):
        #split of folder structure
        return "".join(path.split("/")[3:])
    
    def playsong(self):
        """find the selected index and play corresponding song"""
        selected_song = self.playlist.get(tk.ACTIVE)
        songs = self.playlist.get(0,tk.END)
        if selected_song in songs:
            current_song_index = songs.index(selected_song)
        else: 
            self.track.set("")
            return
        active_song=self.songs[current_song_index]        
        if not Path(active_song).is_file():
            self.track.set("")
            return
        self.track.set(selected_song)
        self.status.set(PLAYING)
        
        #save time of current song
        sound = pygame.mixer.Sound(active_song)
        self.track_time = sound.get_length() 
        print("song is ", self.track_time, " s long")
        # load song
        pygame.mixer.music.load(active_song)
        #overwrite start time
        self.start_time = time.time()
        self.after(2300, self.update_progress)
        pygame.mixer.music.play()
        
        
    def stopsong(self):
        self.status.set(STOPPED)
        pygame.mixer.music.stop()
    
        
    def update_progress(self):
        if self.progressbar is None:
            print("progressbar is not available")
            return
        
        new_value = time.time() - self.start_time
        progress_percent = (new_value / self.track_time) * 100
        if progress_percent >= 98.0:
            progress_percent = 100.0
        
        # Update the progress bar
        self.progressbar["value"] = int(progress_percent)
        
        self.after(2300, self.update_progress)

        
