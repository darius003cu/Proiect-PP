import serial
import matplotlib.pyplot as plt
import numpy as np

def plotTest():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    plt.show()

def plotUSART():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    plt.xlabel("Timp [s]")
    plt.ylabel("Tensiune [V]")
    plt.show()

def openSerial():
    global ser
    ser = serial.Serial("COM3", 9600, timeout = 0)

def readLine():
    if ser and ser.in_waiting:
       line = ser.read().decode().strip()
       return line
    return None
