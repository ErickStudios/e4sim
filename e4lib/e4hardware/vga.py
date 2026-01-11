class e4hardware_vga:
    # el segmento donde esta el color del vga
    vga_offset = 0xB82
    # el color de la consola
    @staticmethod
    def color_console(col: int):
        # negro oscuro
        if (col == 0): return "#000000"
        # azul oscuro
        elif (col == 1): return "#000066"
        # verde oscuro
        elif (col == 2): return "#006600"
        # cian oscuro
        elif (col == 3): return "#006666"
        # rojo oscuro
        elif (col == 4): return "#660000"
        # magenta oscuro
        elif (col == 5): return "#660066"
        # amarillo oscuro
        elif (col == 6): return "#666600"
        # gris
        elif (col == 7): return "#666666"
        # negro brillante
        elif (col == 8): return "#434343"
        # azul
        elif (col == 9): return "#6464ff"
        # verde
        elif (col == 10): return "#62ff62"
        # cian
        elif (col == 11): return "#74ffff"
        # rojo
        elif (col == 12): return "#ff3434"
        # magenta
        elif (col == 13): return "#ff00ff"
        # amarillo
        elif (col == 14): return "#ffff00"
        # blanco
        elif (col == 15): return "#ffffff"
