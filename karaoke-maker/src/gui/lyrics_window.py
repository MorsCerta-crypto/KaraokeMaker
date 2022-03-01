from tkinter import Tk,StringVar,N,Label,mainloop,CENTER

def show_lyrics(lyrics): 

    master = Tk() 
    master.title("Lyrics")
    master.geometry("600x1000+100+100")
    master.configure(bg='light grey') 

    result = StringVar()
    result.set(lyrics)
    
    Label(master, text="", textvariable=result, 
        bg="light grey").grid(sticky=N) 

    mainloop()
           
if __name__ == "__main__":
    show_lyrics("Songname\n\nhere are the \nlyrics")

