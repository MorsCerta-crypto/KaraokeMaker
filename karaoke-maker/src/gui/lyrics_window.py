from tkinter import Tk,StringVar,N,Label,mainloop,CENTER,Toplevel

def show_lyrics(lyrics,root): 

    master = Toplevel(root) 
    master.title("Lyrics")
    master.geometry("800x1000+100+100")
    master.configure(bg='light grey') 

    result = StringVar()
    result.set(lyrics)
    
    Label(master, text="", textvariable=result, 
        bg="light grey",font=("times new roman",15,"bold")).grid(sticky=N) 

    mainloop()
           
if __name__ == "__main__":
    root = Tk()
    show_lyrics("Songname\n\nhere are the \nlyrics",root)

