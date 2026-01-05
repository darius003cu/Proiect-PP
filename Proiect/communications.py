import serial
import matplotlib.pyplot as plt
import numpy as np

import serial

ser = serial.Serial(
    port="COM3",       
    baudrate=9600,
    timeout=1
)

print("Connected")

while True:
    line = ser.readline()
    if line:
        value = int(line.decode().strip())
        print(value)


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



