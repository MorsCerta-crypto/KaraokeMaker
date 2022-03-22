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
        
        #Frame for running track
        trackframe = ttk.Frame(self,relief=tk.GROOVE)
        trackframe.place(x=0,y=0,width=500,height=100)
        ttk.Label(trackframe,
                  textvariable=self.track,
                  width=20,
                  font=("Arial",18)).grid(row=0,column=0,padx=5,pady=5)
        ttk.Label(trackframe,
                  textvariable=self.status,
                  font=("Arial",15)).grid(row=0,column=1,padx=5,pady=5)
        self.progressbar = ttk.Progressbar(trackframe,
                                           length=150,
                                           maximum=100,
                                           orient="horizontal",
                                           mode="determinate")
        self.progressbar.grid(row=1,columnspan=2,padx=5,pady=5)

        #frame for buttons
        buttonframe = ttk.Frame(self,relief=tk.GROOVE)
        buttonframe.place(x=0,y=100,width=500,height=200)
        ttk.Button(buttonframe,
                   text="PLAYSONG",
                   command=self.playsong,
                   width=10).grid(row=0,column=0,padx=2,pady=2)
        ttk.Button(buttonframe,
                   text="PAUSE",
                   command=self.pausesong,
                   width=9).grid(row=0,column=1,padx=2,pady=2)
        ttk.Button(buttonframe,
                   text="STOPSONG",
                   command=self.stopsong,
                   width=10).grid(row=0,column=2,padx=2,pady=2)
        ttk.Button(buttonframe,
                   text="NEXT SONG",
                   command=self.nextsong,
                   width=10).grid(row=0,column=3,padx=2,pady=2)
        
        #frame for Playlist
        songsframe = ttk.Frame(self,relief=tk.GROOVE)
        songsframe.place(x=500,y=0,width=300,height=200)
        scrol_y = tk.Scrollbar(songsframe,orient=tk.VERTICAL,relief=tk.GROOVE)
        self.playlist = tk.Listbox(songsframe,
                                   yscrollcommand=scrol_y.set,
                                   selectbackground="gold",
                                   selectmode=tk.SINGLE,
                                   font=("Arial",12),
                                   bg="white",
                                   fg="blue",
                                   bd=5,
                                   relief=tk.GROOVE)
        scrol_y.pack(side=tk.RIGHT,fill=tk.BOTH)
        scrol_y.config(command=self.playlist.yview)
        self.playlist.pack(fill=tk.BOTH,side=tk.RIGHT,expand=1,padx=2,pady=2)
        print("made music player")
        
    
    def nextsong(self):
        active = self.playlist.get(tk.ACTIVE)
        if active is None:
            self.stopsong()
            
        current_song_index = self.playlist.get(0,tk.END).index(active)
        self.playlist.delete(current_song_index)
        self.playlist.activate(current_song_index-1)
        print("next song:", self.playlist.get(current_song_index-1))
        if self.playlist.get(current_song_index-1) is None:
            self.stopsong()
            self.playlist.delete(current_song_index)
        else: 
            self.playsong()
        
    def append_song(self,track):
        self.playlist.insert(tk.END,track)

    def playsong(self):
        active_song = self.playlist.get(tk.ACTIVE)
        if not active_song:
            self.track.set("")
            return
        if active_song.endswith(".mp3"):
            print("mp3 could be skipped")
            #self.nextsong()
        self.track.set(active_song)
        self.status.set(PLAYING)
        
        #save time of current song
        sound = pygame.mixer.Sound(active_song)
        self.track_time = sound.get_length()
        print("song is ", self.track_time, " ms long")
        pygame.mixer.music.load(active_song)
        pygame.mixer.music.play()
        self.after(100, self.update_progress)
        
    def stopsong(self):
        self.status.set(STOPPED)
        pygame.mixer.music.stop()
    
    def pausesong(self):
        self.status.set(PAUSED)
        pygame.mixer.music.pause()
        
    def update_progress(self):
        if self.progressbar is None:
            print("progressbar is not available")
            return
        pos_ms = pygame.mixer.music.get_pos()#self.music.current_position()
        
        print(f"found pos: {pos_ms} and total ms: {self.track_time}")
        if self.track_time != 0:
            progress_percent = pos_ms / float(self.track_time) * 100
            
            # Update the progress bar
            self.progressbar["value"] = progress_percent
        else: 
            print("value set to 0")
            self.progressbar["value"] = 0
        # Schedule next update in 100ms        
        

        


        
def main():
    root = tk.Tk() # In order to create an empty window
    # Passing Root to MusicPlayer Class
    MusicPlayer(root)
    root.mainloop()
    

if __name__ == "__main__":
    main()