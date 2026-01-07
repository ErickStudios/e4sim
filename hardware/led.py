# led.py

import tkinter as tk

def disconect(place: tk.Button):
    place.configure(background="#ffa515")

def hardware_out(place: tk.Button, data: int):
    if data == 1:
        place.configure(background="#00ff9d")
    else:
        place.configure(background="#000000")

def hardware_in(place: tk.Button):
    color:str = place.getvar("background")

    if (color == "#00ff9d"):
        return 1
    else:
        return 0

def update(place: tk.Button, ram:list[int]):
    pass

def open(place: tk.Button):
    place.configure(background="#000000")
