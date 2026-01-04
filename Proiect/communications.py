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


