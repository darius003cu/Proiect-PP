from tkinter import *
import communications as com

com.openSerial()
data = []

window = Tk()
window.geometry("480x320")
window.title("Voltage Graph v0.0.2")
window.resizable(False, False)

def mainWindow():
    mainTitle = Label(window, text = "Grafic Tensiune-ADC", font = ("Times New Roman", 14), pady = 10, padx = 40)
    mainTitle.grid(row = 0, column = 0)
    buttonFrame = Frame(window)
    buttonFrame.grid(row = 1, column = 0)
    plotButton = Button(buttonFrame, text = "Open Plot")
    plotButton.grid(row = 0, column = 0)
    debugButton = Button(buttonFrame, text = "Debug Plot", command = com.plotTest)
    debugButton.grid(row = 1, column = 0)


def debugWindow():
    debugWin = Toplevel()
    debugWin.geometry("400x300")
    debugWin.title("Debugging for plots")
    button1 = Button(debugWin, text = "Open simple plot", command = com.plotTest)
    button1.grid(row = 3, column = 1)
    button2 = Button(debugWin, text = "Open main plot", command = com.plotUSART)
    button2.grid(row = 4, column = 1)
    debugWin.mainloop()
    
def exportValues(log):
    while True:
        line = com.readLine()
        if not line:
            break
        data.append(line)
    
    if len(data) >= 10:
        for val in data:
            log.insert(END, val + "\n")
        log.see(END)
        data.clear()

    window.after(1, lambda: exportValues(log))

def USARTlogging():
    statusTitle = Label(window, text = "Status: TESTING         Baud rate: 9600")
    statusTitle.grid(row = 0, column = 1)
    log = Text(window, width = 25, height = 15)
    log.grid(row = 1, column = 1)
    logFrame = Frame(window)
    logFrame.grid(row = 2, column = 1)
    logButton = Button(logFrame, text = "START", command = lambda: exportValues(log))
    logButton.grid(row = 0, column = 0, padx = 10, pady = 2)
    logConvertType = Button(logFrame, text = "Convert to VOLTAGE")
    logConvertType.grid(row = 0, column = 1, padx = 10, pady = 2)
    window.mainloop()

