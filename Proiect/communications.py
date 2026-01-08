import serial

ser = None

def openSerial(portName, baudRate): 
    global ser
    try:
        ser = serial.Serial(portName, baudRate, timeout=0)
        return True
    except serial.SerialException:
        ser = None
        return False
    
def readLine():
    if ser and ser.in_waiting:
       line = ser.readline()
       if line:
        return line
    return None



