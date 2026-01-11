# importar tkinder
import tkinter as tk
# estilo de pbc
class e4hardware_pins_style:
    def __init__(self):
        pass
    # hace una coneccion de pins
    @staticmethod
    def _make_serpiente1_(canvas: tk.Canvas, x: int, y: int, prts: int):
        # poner los pins
        for i in range(prts):
            # hacer pin
            e4hardware_pins_style.make_pin(canvas, x + (i * 6), y)
    # hace un pin
    @staticmethod
    def make_pin(canvas: tk.Canvas, x: int, y: int):
        # dibuja la base del pin (pequeño rectángulo)
        canvas.create_rectangle(x - 2, y + 2, x + 2, y + 4, fill="#363636")
        # dibuja la línea vertical del pin
        canvas.create_line(
            x, y - 2, x, y + 8,
            fill="#282828",     # color de la línea
            width=3,            # grosor del trazo
            dash=(4, 2),        # estilo punteado (opcional)
            capstyle="round",   # extremos: 'butt', 'round', 'projecting'
            joinstyle="round"   # unión de segmentos (si hay más puntos)
        )
