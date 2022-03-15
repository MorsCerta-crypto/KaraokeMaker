from tkinter import (StringVar,Toplevel,LabelFrame,Label,
                     Button,Scrollbar,Listbox,VERTICAL,RIGHT,
                     Tk,BOTH,END,ACTIVE,SINGLE,GROOVE,Y)
import pygame

PAUSED = "PAUSED"
PLAYING = "PLAYING"
STOPPED = "STOPPED"


class MusicPlayer(Toplevel):
    
    def __init__(self,root):
        super().__init__(root)
        self.title("MusicPlayer")
        self.geometry("950x250+710+10")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        pygame.init()
        pygame.mixer.init()
        self.track = StringVar()
        self.status = StringVar()
        self.status.set(STOPPED)
        trackframe = LabelFrame(self,text="Song Track",font=("times new roman",15,"bold"),bg="Navyblue",fg="white",bd=5,relief=GROOVE)
        trackframe.place(x=0,y=0,width=600,height=100)
        Label(trackframe,textvariable=self.track,width=40,font=("times new roman",18,"bold"),bg="Orange",fg="gold").grid(row=0,column=0,padx=10,pady=5)
        Label(trackframe,textvariable=self.status,font=("times new roman",15,"bold"),bg="orange",fg="gold").grid(row=0,column=1,padx=10,pady=5)

        buttonframe = LabelFrame(self,text="Control Panel",font=("times new roman",15,"bold"),bg="grey",fg="white",bd=5,relief=GROOVE)
        buttonframe.place(x=0,y=100,width=600,height=100)
        Button(buttonframe,text="PLAYSONG",command=self.playsong,width=11,height=1,font=("times new roman",15,"bold"),fg="navyblue",bg="pink").grid(row=0,column=0,padx=10,pady=5)
        Button(buttonframe,text="PAUSE",command=self.pausesong,width=9,height=1,font=("times new roman",15,"bold"),fg="navyblue",bg="pink").grid(row=0,column=1,padx=10,pady=5)
        Button(buttonframe,text="UNPAUSE",command=self.unpausesong,width=11,height=1,font=("arial",15,"bold"),fg="navyblue",bg="pink").grid(row=0,column=2,padx=10,pady=5)
        Button(buttonframe,text="STOPSONG",command=self.stopsong,width=11,height=1,font=("arial",15,"bold"),fg="navyblue",bg="pink").grid(row=0,column=3,padx=10,pady=5)
        Button(buttonframe,text="NEXT SONG",command=self.nextsong,width=11,height=1,font=("arial",15,"bold"),fg="navyblue",bg="pink").grid(row=0,column=4,padx=10,pady=5)
        songsframe = LabelFrame(self,text="Song Playlist",font=("times new roman",15,"bold"),bg="grey",fg="white",bd=5,relief=GROOVE)
        songsframe.place(x=600,y=0,width=400,height=200)
        scrol_y = Scrollbar(songsframe,orient=VERTICAL)
        self.playlist = Listbox(songsframe,yscrollcommand=scrol_y.set,selectbackground="gold",selectmode=SINGLE,font=("times new roman",12,"bold"),bg="silver",fg="navyblue",bd=5,relief=GROOVE)
        scrol_y.pack(side=RIGHT,fill=Y)
        scrol_y.config(command=self.playlist.yview)
        self.playlist.pack(fill=BOTH)
        
    
    def nextsong(self):
        active = self.playlist.get(ACTIVE)
        if active is None:
            self.stopsong()
            
        current_song_index = self.playlist.get(0,END).index(active)
        self.playlist.delete(current_song_index)
        self.playlist.activate(current_song_index-1)
        print("next song:", self.playlist.get(current_song_index-1))
        if self.playlist.get(current_song_index-1) is None:
            self.stopsong()
            self.playlist.delete(current_song_index)
            
        else: 
            self.playsong()
        
    def append_song(self,track):
        self.playlist.insert(END,track)

    def playsong(self):
        active_song = self.playlist.get(ACTIVE)
        if not active_song:
            return
        if active_song.endswith(".mp3"):
            print("mp3 could be skipped")
            #self.nextsong()
        self.track.set(active_song)
        self.status.set(PLAYING)
        pygame.mixer.music.load(active_song)
        pygame.mixer.music.play()
        
    def stopsong(self):
        self.status.set(STOPPED)
        pygame.mixer.music.stop()
    
    def pausesong(self):
        self.status.set(PAUSED)
        pygame.mixer.music.pause()
    
    def unpausesong(self):
        self.status.set(PLAYING)
        pygame.mixer.music.unpause()
        
    def on_closing(self):
        self.stopsong()
        #self.destroy()


        
def main():
    root = Tk() # In order to create an empty window
    # Passing Root to MusicPlayer Class
    MusicPlayer(root)
    root.mainloop()
    

if __name__ == "__main__":
    main()