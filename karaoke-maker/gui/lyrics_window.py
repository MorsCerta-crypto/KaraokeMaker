import tkinter as tk# Tk,StringVar,N,Label,mainloop
from tkinter import ttk

BAD_WORDS = ["embed","lyrics"]

class LyricsWindow(ttk.Frame):
    def __init__(self,root):
        super().__init__(root)
        
        lyrics_frame = ttk.Frame(self)
        header = ttk.Label(lyrics_frame, text="Lyrics",font=("arial",22))
        header.grid(row=0,column=0)
        self.Lyrics = ttk.Label(lyrics_frame, text="", 
                                font=("arial",16))
        self.Lyrics.grid(row=1,rowspan=2, column=0,sticky=tk.NSEW,padx=20,pady=20,ipady=20,ipadx=20) 
        
        lyrics_frame.grid(sticky=tk.NSEW,rowspan=3)
        lyrics_frame.grid_rowconfigure(index=1,weight=1,minsize=50)
        
        
    def set_lyrics(self,text):
        """changes text of lyrics window"""
        
        value = self._preprocess_text(text)
        if self.Lyrics is not None:
            self.Lyrics["text"] = value
        

    def _preprocess_text(self,text):
        """removes unwanted words from text"""
        
        for word in BAD_WORDS:
            if word in text.lower():
                text = text.replace(word,"\n")
        return text
        
        


