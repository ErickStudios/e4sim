# led.py

import tkinter as tk

def disconect(place: tk.Button):
    place.configure(background="#ffa515")
    pass

def update(place: tk.Button, ram:list[int]):
    if ram[0x08] == 1:
        place.configure(background="#00ff9d")
    else:
        place.configure(background="#000000")

def open(place: tk.Button):
    pass