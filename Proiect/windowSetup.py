from tkinter import *
import communications

def mainWindow():
    window = Tk()
    window.geometry("640x320")
    window.title("Voltage Graph v0.0.1")
    button = Button(window, text = "Open debug window", command = debugWindow)
    button.pack()
    window.mainloop()

def debugWindow():
    debugWin = Toplevel()
    debugWin.geometry("400x300")
    debugWin.title("Debugging for plots")
    button1 = Button(debugWin, text = "Open simple plot", command = communications.plotTest)
    button1.pack(side = "top", anchor = "center", pady = 120)
    button2 = Button(debugWin, text = "Open main plot", command = communications.plotUSART)
    button2.pack(side = "top", anchor = "center", pady = 140)
    debugWin.mainloop()
