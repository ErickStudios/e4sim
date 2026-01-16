# importar tkinder
import tkinter as tk
# ventana de ver memoria
class e4simapp_memview(tk.Toplevel):
    # inicializacion
    def __init__(self, master, vm):
        # init
        super().__init__(master)
        # la maquina virtual
        self.vm = vm
        # el titulo
        self.title("e4sim - memory inspector")
        # fondo
        self.configure(bg="#1E1E1E")
        # widget para mostrar la memoria
        self.text = tk.Text(self, width=80, height=25, bg="#1E1E1E", fg="#ffffff")
        # el texto
        self.text.pack(fill="both", expand=True)
        # refrescar cada cierto tiempo
        self.update_mem()
    # actualiza la memoria
    def update_mem(self):
        # guardar posición actual
        pos = self.text.yview()
        # el delete 1.0
        self.text.delete("1.0", tk.END)
        # iterar la memoria
        for i in range(0, len(self.vm.mem), 16):
            self.update()
            # el bloque
            bloque = self.vm.mem[i:i+16]
            # hexadecimales
            hexs = " ".join(f"{b:02X}" for b in bloque)
            # caracteres ASCII (imprimibles → mostrar, no imprimibles → '.')
            chars = "".join(chr(b) if 32 <= b < 127 else "." for b in bloque)
            # insertar línea estilo hex dump
            self.text.insert(tk.END, f"{i:04X}: {hexs:<48} {chars}\n")
        # restaurar posición
        self.text.yview_moveto(pos[0])
        # actualizar memoria
        self.after(500, self.update_mem)