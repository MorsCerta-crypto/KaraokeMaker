import tkinter as tk# Tk,StringVar,N,Label,mainloop
from tkinter import ttk

BAD_WORDS = ["embed","lyrics"]

class LyricsWindow(ttk.Frame):
    def __init__(self,root):
        super().__init__(root)
        
        lyrics_frame = ttk.Frame(self)
        header = ttk.Label(lyrics_frame, text="Lyrics",font=("arial",22))
        header.grid(row=0,column=0)
        scrol_y = tk.Scrollbar(lyrics_frame,orient=tk.VERTICAL,relief=tk.GROOVE)
        self.Lyrics = tk.Listbox(lyrics_frame, 
                                font=("courier 11",16),
                                yscrollcommand=scrol_y.set,
                                selectmode=tk.NONE)
        
        self.Lyrics.grid(row=1,
                         rowspan=2,
                         column=0,
                         sticky=tk.NSEW,
                         padx=5, 
                         pady=5,
                         ipady=20,
                         ipadx=20) 
    
        scrol_y.grid(row=1,rowspan=2,column=1,sticky=tk.NSEW)
        scrol_y.config(command=self.Lyrics.yview)
        
        lyrics_frame.grid(column=0,row=0,sticky=tk.NSEW,rowspan=3)
        lyrics_frame.grid_rowconfigure(index=1,weight=1,minsize=50)
        lyrics_frame.grid_columnconfigure(index=0,weight=1,minsize=450)
        
        
    def set_lyrics(self,text):
        """changes text of lyrics window"""
        
        lines:list = self._preprocess_text(text)
        self.Lyrics.delete(0,tk.END)

        if self.Lyrics is not None:
            for line in lines:
                self.Lyrics.insert(tk.END,f" {line:20} ")
        

    def _preprocess_text(self,text:str)->list[str]:
        """removes unwanted words from text"""
        
        
        clean_text = []
        # check bad words
        
        for line in text.split("\n"):
            for word in BAD_WORDS:
                ind = line.lower().find(word)
                if ind != -1:
                    line = line.replace(line[ind:ind+len(word)]," ",-1)
                
            # devide line if it is too long
            if len(line)>60 and " " in line[45:60]:
                ind = line[45:60].find(" ")
                place = 45 + ind
                clean_text.append(line[:place])
                clean_text.append(" -> "+line[place:])
            else:         
                clean_text.append(line)
        return clean_text
        
        


