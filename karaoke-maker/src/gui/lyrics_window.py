from tkinter import Tk,StringVar,N,Label,mainloop

def show_lyrics(lyrics,root): 

    master = root#Toplevel(root) 
    master.title("Lyrics")
    master.geometry("700x1000") # left top
    master.configure(bg='light grey') 

    result = StringVar()
    result.set(lyrics)
    
    Label(master, text="", textvariable=result, 
        bg="light grey",font=("arial",14,"bold")).grid(sticky=N,padx=20,pady=20) 

    mainloop()
           
if __name__ == "__main__":
    root = Tk()
    show_lyrics("Songname\n\nhere are the \nlyrics",root)

