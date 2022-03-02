from tkinter import (StringVar,Toplevel,LabelFrame,Label,
                     Button,Scrollbar,Listbox,VERTICAL,RIGHT,
                     Tk,BOTH,END,ACTIVE,SINGLE,GROOVE)
import pygame

class MusicPlayer(object):
    
    def __init__(self,root):
        self.root = Toplevel(root)
        self.root.title("MusicPlayer")
        self.root.geometry("1000x250")
        pygame.init()
        pygame.mixer.init()
        self.track = StringVar()
        self.status = StringVar()

        trackframe = LabelFrame(self.root,text="Song Track",font=("times new roman",15,"bold"),bg="Navyblue",fg="white",bd=5,relief=GROOVE)
        trackframe.place(x=0,y=0,width=600,height=100)
        songtrack = Label(trackframe,textvariable=self.track,width=40,font=("times new roman",18,"bold"),bg="Orange",fg="gold").grid(row=0,column=0,padx=10,pady=5)
        trackstatus = Label(trackframe,textvariable=self.status,font=("times new roman",18,"bold"),bg="orange",fg="gold").grid(row=0,column=1,padx=10,pady=5)

        buttonframe = LabelFrame(self.root,text="Control Panel",font=("times new roman",15,"bold"),bg="grey",fg="white",bd=5,relief=GROOVE)
        buttonframe.place(x=0,y=100,width=600,height=100)
        playbtn = Button(buttonframe,text="PLAYSONG",command=self.playsong,width=10,height=1,font=("times new roman",16,"bold"),fg="navyblue",bg="pink").grid(row=0,column=0,padx=10,pady=5)
        playbtn = Button(buttonframe,text="PAUSE",command=self.pausesong,width=8,height=1,font=("times new roman",16,"bold"),fg="navyblue",bg="pink").grid(row=0,column=1,padx=10,pady=5)
        playbtn = Button(buttonframe,text="UNPAUSE",command=self.unpausesong,width=10,height=1,font=("times new roman",16,"bold"),fg="navyblue",bg="pink").grid(row=0,column=2,padx=10,pady=5)
        playbtn = Button(buttonframe,text="STOPSONG",command=self.stopsong,width=10,height=1,font=("times new roman",16,"bold"),fg="navyblue",bg="pink").grid(row=0,column=3,padx=10,pady=5)

        songsframe = LabelFrame(self.root,text="Song Playlist",font=("times new roman",15,"bold"),bg="grey",fg="white",bd=5,relief=GROOVE)
        songsframe.place(x=600,y=0,width=400,height=200)
        scrol_y = Scrollbar(songsframe,orient=VERTICAL)
        self.playlist = Listbox(songsframe,yscrollcommand=scrol_y.set,selectbackground="gold",selectmode=SINGLE,font=("times new roman",12,"bold"),bg="silver",fg="navyblue",bd=5,relief=GROOVE)
        scrol_y.pack(side=RIGHT,fill=Y)
        scrol_y.config(command=self.playlist.yview)
        self.playlist.pack(fill=BOTH)
        
    
    def append_song(self,track):
        self.playlist.insert(END,track)

    def playsong(self):
        print(self.playlist.get(ACTIVE))
        if self.playlist.get(ACTIVE) is None:
            raise ValueError("no song given")
        self.track.set(self.playlist.get(ACTIVE))
        self.status.set("-Playing")
        pygame.mixer.music.load(self.playlist.get(ACTIVE))
        pygame.mixer.music.play()
        
    def stopsong(self):
        self.status.set("-Stopped")
        pygame.mixer.music.stop()
    
    def pausesong(self):
        self.status.set("-Paused")
        pygame.mixer.music.pause()
    
    def unpausesong(self):
        self.status.set("-Playing")
        pygame.mixer.music.unpause()
        
def main():
    root = Tk() # In order to create an empty window
    # Passing Root to MusicPlayer Class
    MusicPlayer(root)
    root.mainloop()
    

if __name__ == "__main__":
    main()