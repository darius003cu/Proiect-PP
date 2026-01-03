from tkinter import *

def mainWindow():
    window = Tk()
    mainTitle = Text(window, padx = 5, pady = 5)
    mainTitle.insert(INSERT, "Voltage")
    mainTitle.pack()
    window.geometry("640x320")
    window.title("Voltage Graph v0.0.1")
    window.mainloop()

