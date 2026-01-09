import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime
import communications as com
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
matplotlib.use("TkAgg")

global BAUD_RATE
BAUD_RATE = 9600

global SERIAL_PORT
SERIAL_PORT = "COM3" 

def setPort(port):
    global SERIAL_PORT
    SERIAL_PORT = port
    print(f"Port selected: {SERIAL_PORT}")
    
    if com.ser and com.ser.is_open:
        com.ser.close()
        com.ser = None
        messagebox.showinfo("Port Changed", f"Portul a fost schimbat la {port}. Apasati START pentru repornire.")

global isRunning
isRunning = False
recentValues = []

window = Tk()
window.geometry("800x480")
window.title("Grafic Tensiune-ADC")
window.resizable(False, False)

baudVar = StringVar()
baudVar.set("Baud rate: 9600")

def setBaud(rate):
    global BAUD_RATE
    BAUD_RATE = rate
    baudVar.set(f"Baud rate: {BAUD_RATE}")

    print(f"Baud rate set to: {BAUD_RATE}")
    if isRunning:
        messagebox.showinfo("Baud Rate schimbat", "Apasati STOP urmat de START pentru a aplica noua viteza.")

    elif com.ser and com.ser.is_open:
        com.ser.close()
        com.ser = None

def mainWindow():
    menubar = Menu(window)    
    portMenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Port", menu=portMenu)
    
    selected_port_var = StringVar(value=SERIAL_PORT)

    def on_port_select():
        new_port = selected_port_var.get()
        setPort(new_port)

    portMenu.add_radiobutton(label="COM3", value="COM3", variable=selected_port_var, command=on_port_select)
    portMenu.add_radiobutton(label="COM4", value="COM4", variable=selected_port_var, command=on_port_select)
    portMenu.add_radiobutton(label="COM5", value="COM5", variable=selected_port_var, command=on_port_select)
    
    optionMenu = Menu(menubar, tearoff=0) 
    menubar.add_cascade(label="Baud rate", menu=optionMenu)
    optionMenu.add_command(label="9600", command=lambda: setBaud(9600))
    optionMenu.add_command(label="115200", command=lambda: setBaud(115200))
    window.config(menu=menubar)

def createLivePlot(parent, adcLog, voltLog, clearButton, avgLabel, saveButton, statusLabel, toggleButton):
    fig = Figure(figsize=(4, 4), dpi=100)
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)

    ax.set_title("Tensiune")
    ax.set_xlabel("Esantioane")
    ax.set_ylabel("Tensiune [V]")
    ax.grid(True, linestyle='--', alpha=0.6)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    xData = []
    yData = []
    
    fullSessionData = [] 

    avgBuffer = [] 
    serialBuffer = "" 

    line, = ax.plot([], [], lw=2, color='#1f77b4')

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def saveData():
        if not fullSessionData:
            messagebox.showwarning("Date neexistente", "Nu exista date ce pot fi salvate!")
            return
            
        filename = filedialog.asksaveasfilename(
            initialdir="/",
            title="Save Database",
            filetypes=(("SQLite Database", "*.db"), ("All Files", "*.*")),
            defaultextension=".db"
        )
        
        if filename:
            try:
                conn = sqlite3.connect(filename)
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS voltage_readings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sample_number INTEGER,
                        voltage REAL,
                        timestamp TEXT
                    )
                """)
                
                cursor.executemany("""
                    INSERT INTO voltage_readings (sample_number, voltage, timestamp)
                    VALUES (?, ?, ?)
                """, fullSessionData)
                
                allVoltages = [row[1] for row in fullSessionData]
                rawAverage = sum(allVoltages) / len(allVoltages)
                globalAverage = round(rawAverage, 3)
                
                saveTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS session_summary (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        save_time TEXT,
                        total_samples INTEGER,
                        global_average_voltage REAL
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO session_summary (save_time, total_samples, global_average_voltage)
                    VALUES (?, ?, ?)
                """, (saveTime, len(fullSessionData), globalAverage))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", 
                    f"S-au salvat {len(fullSessionData)} de valori.\n"
                    f"Tensiune medie globala: {globalAverage:.3f} V\n"
                    f"Salvat la: {saveTime}")
                
            except Exception as e:
                messagebox.showerror("Eroare", f"Nu s-a putut salva baza de date: {e}")

    saveButton.config(command=saveData)

    def clearPlot():
        xData.clear()
        yData.clear()
        fullSessionData.clear() 
        recentValues.clear()
        avgBuffer.clear()
        
        avgLabel.config(text="Medie (50): --- V")
        line.set_data([], [])
        ax.set_xlim(0, 10)
        canvas.draw_idle()

        adcLog.delete("1.0", END)
        voltLog.delete("1.0", END)

    clearButton.config(command=clearPlot)

    def updatePlot():
        nonlocal serialBuffer 
        global recentValues
        global isRunning

        if isRunning and com.ser and com.ser.is_open:
            try:
                if com.ser.in_waiting > 0:
                    newData = com.ser.read(com.ser.in_waiting).decode('utf-8', errors='ignore')
                    serialBuffer += newData

                    if '\n' in serialBuffer:
                        lines = serialBuffer.split('\n')
                        
                        if len(lines) >= 2:
                            lastCompleteLine = lines[-2] 

                            if lastCompleteLine:
                                adc = int(lastCompleteLine.strip())

                                adcLog.insert(END, f"{adc}\n")
                                adcLog.see(END)
                                
                                voltageVal = adc * 5 / 1024
                                voltLog.insert(END, f"{voltageVal:.2f}V\n")
                                voltLog.see(END)
                                
                                
                                voltage = adc * 5 / 1024
                                    
                                if len(xData) > 0:
                                    newX = xData[-1] + 1
                                else:
                                    newX = 0

                                sampleTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] 
                                fullSessionData.append((newX, voltage, sampleTime))

                                avgBuffer.append(voltage)
                                if len(avgBuffer) >= 50:
                                    avgVal = sum(avgBuffer) / len(avgBuffer)
                                    avgLabel.config(text=f"Medie (50): {avgVal:.2f} V")
                                    avgBuffer.clear()

                                xData.append(newX)
                                yData.append(voltage)

                                if len(xData) > 100:
                                    xData.pop(0)
                                    yData.pop(0)
                                

                                line.set_data(xData, yData)
                                ax.set_ylim(0, 5.5)
                                pageStart = (newX // 100) * 100
                                ax.set_xlim(pageStart, pageStart + 100)
                                canvas.draw_idle()

            except (com.serial.SerialException, OSError) as e:
                print(f"Critical Error: Device disconnected - {e}")
                statusLabel.config(text="Status: DISCONNECTED", fg="red")
                toggleButton.config(text="START", bg ="#dddddd", fg="black")
                
                isRunning = False 
                
                if com.ser:
                    com.ser.close()
                    com.ser = None
                
                messagebox.showerror("Eroare Conexiune", "Conexiunea USB a fost intrerupta!")
                
            except ValueError:
                pass 
            except Exception as e:
                print(f"General Error: {e}")

        parent.after(20, updatePlot)

    updatePlot() 

def toggleSampling(statusLabel, toggleBtn):
    global isRunning
    
    if isRunning:
        isRunning = False
        statusLabel.config(text="Status: PAUSED", fg="red")
        toggleBtn.config(text="START", bg="#dddddd", fg="black") 
        
    else:
        if not com.ser:
            if not com.openSerial(SERIAL_PORT, BAUD_RATE):
                messagebox.showwarning("Error", "Serial neconectat")
                return

        isRunning = True
        com.ser.reset_input_buffer()
        statusLabel.config(text="Status: RUNNING", fg="green")
        toggleBtn.config(text="STOP", bg="red", fg="white")

def USARTlogging():
    serialFrame = Frame(window)
    serialFrame.grid(row=0, column=0)
    statusTitle = Label(serialFrame, text="DISCONNECTED") 
    statusTitle.grid(row=0, column=0) 
    adcBox = Text(serialFrame, width=20, height=15) 
    adcBox.grid(row=1, column=0, padx=10) 
    baudTitle = Label(serialFrame, textvariable=baudVar) 
    baudTitle.grid(row=0, column=1) 
    voltageBox = Text(serialFrame, width=20, height=15) 
    voltageBox.grid(row=1, column=1, padx=10)
    avgLabel = Label(serialFrame, text="Medie (50): --- V", font=("Arial", 12, "bold"), fg="blue")
    avgLabel.grid(row=2, column=0, columnspan=2, pady=5)
    buttonFrame = Frame(window)
    buttonFrame.grid(row=1, column=0)
    toggleButton = Button(buttonFrame, text="START", width=10, font=("Arial", 10, "bold"))
    toggleButton.config(command=lambda: toggleSampling(statusTitle, toggleButton))
    toggleButton.grid(row=0, column=0, padx=10)
    saveButton = Button(buttonFrame, text="SAVE DB", width=10, font=("Arial", 10, "bold"))
    saveButton.grid(row=0, column=1, padx=10)
    clearButton = Button(buttonFrame, text="CLEAR", width=10, font=("Arial", 10, "bold"))
    clearButton.grid(row=0, column=2, padx=10)
    plotFrame = Frame(window)
    plotFrame.grid(row=0, column=1, rowspan=2, padx=10, pady=10)
    
    createLivePlot(plotFrame, adcBox, voltageBox, clearButton, avgLabel, saveButton, statusTitle, toggleButton)
    
    window.mainloop()


