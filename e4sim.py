# la libreria de e4asm
import e4lib.assambler as e4asm
# la app de debug
from e4lib.e4sim_app.memview import e4simapp_memview as DebugWindow
# el tooltip
from e4lib.tootltip import ToolTip as e4app_tooltip

# el hardware
from e4lib.e4arch.hardware import e4arch_hardware as Hardware
# la libreria de los colores
from e4lib.e4hardware.vga import e4hardware_vga
# la tarjeta de lan
from e4lib.e4hardware.eic3045 import e4hardware_eic3045
# la libreria para dibujar pines
from e4lib.e4hardware.pbc import e4hardware_pins_style as stylepbc

# el fs
from e4lib.e4fs.fs import e4fs as filesystem
# la maquina virtual
from e4lib.e4arch.arch import e4arch as VM

# para los parametros
from sys import argv
# importar el os
import os
# importar el stack
import queue
# importar los treadigns
import threading

# el para guis
import tkinter as tk
# el dialogo de archivos
from tkinter import filedialog
# el dialogo de texto
from tkinter import simpledialog

# colores de la consola
color_console = e4hardware_vga.color_console
# el queue de las teclas
key_queue = queue.Queue()
# el segmento donde esta el vga
vga_offset = e4hardware_vga.vga_offset

# pide un texto
def pedir_texto():
    # abre el cuadro de diálogo y retorna lo que el usuario escribió
    texto = simpledialog.askstring("Input", "Escribe tu linea de codigo ensamblador")
    # retornar
    return texto
# clase de la aplicacion
class Erick4004SimuApp:
    # inicializar
    def __init__(self):
        # el programa actual
        self.current_program:list[int] = list()
        # el usb index
        self.usb_index = 0
        # la maquina virtual
        self.VirtualMachine = VM()
        # el vidoff
        self.vidoff = 0
        # la pc donde esta la vm
        self.VirtualMachine.pc_fetch = self
        # el usb buffer
        self.usb_buffer = bytearray()
        # el index de programa
        self.program_index = 0
        # el buffer de programa
        self.program_buffer = bytearray()
        # archivo de firmware
        self.fd_file = os.path.join(os.getcwd(), "e4lib", "firmware", "main.asm")

        # la direccion base de la tabla idt, solo es el binario
        self.idt_table_base = 0
        # los offsets a las interrupciones
        self.offsets_idt:dict[int, int] = dict()
        # actual idt index a setear
        self.current_idt_index = 0
        # el tamaño del programa
        self.current_idt_size = 0

        # tarjeta de red
        self.net = e4hardware_eic3045()

        # Ventana principal
        self.root = tk.Tk()
        # el titulo
        self.root.title("e4sim - pc virtual")
        # geometria
        self.root.geometry("450x240")
        # el fondo
        self.root.configure(bg="#1E1E1E")

        # el menu
        self.menu_init(self.root)

        # el label 0
        label0 = tk.Label(self.root, text="\n", background="#1E1E1E", foreground="white")
        # poner el label
        label0.pack(pady=0.1)

        # el pc
        canvas = tk.Canvas(self.root, width=310, height=140, bg="#3E6321")
        # poner el pc
        canvas.pack()

        # el paso
        step = (6*10) + 5
        # ir viendo
        for f in [0, 1, 2.8, 3.8]:
            # x
            x = 0 + step * f
            # hacer los pins
            stylepbc._make_serpiente1_(canvas, x, 130, 10)

        # el paso
        step = (6*10) + 5
        # ir viendo
        for f in [0, 1, 2.8, 3.8]:
            # x
            x = 0 + step * f
            # hacer los pins
            stylepbc._make_serpiente1_(canvas, x, 4, 10)

        # las instrucciones para que no se pierdan
        label1 = tk.Label(self.root, text="Seleccione un componente para modificarlo", background="#1E1E1E", foreground="white")
        # el pack
        label1.pack(pady=0.1)

        # los hardwares
        self.hardwares = [
            Hardware(lambda place, ram: None, lambda place: None),
            Hardware(lambda place, ram: None, lambda place: None),
            Hardware(lambda place, ram: None, lambda place: None),
        ]

        # el codigo original del circuitos pbc
        self.original_pbc_color = "#64A136"
        # el color cuando pasa energia a los cables pbc
        self.passing_energy_pbc_color = "#89D44F"

        # si viene una tecla
        self.keyboard_comming = False
        # el canvas
        self.canvas = canvas
        # conexiones pbc 0
        self.pbc_conections = []
        # conexiones pbc 1
        self.pbc_port1_conections = []
        # conexiones pbc 2
        self.pbc_port2_conections = []
        # conexiones pbc 3
        self.pbc_port3_conections = []
        # conexiones pbc 4
        self.pbv_port4_conections = []
        # conexiones pbc 5
        self.pbv_port5_conections = []

        # simulando los circuitos impresos de I/O, para el procesador recibir puertos de la usb, y la usb recibir datos
        # del prosesador

        for i in range(5):
            # crear linea
            line_id = canvas.create_line(3, (20 + (i * 5)), 200, (20 + ((i * 5))), fill="#64A136", width=2)
            # añadir a los pbc
            self.pbc_conections.append(line_id)
        for i in range(5):
            # crear linea
            line_id = canvas.create_line((210+3), (20 + (i * 5)), (210+40), (20 + ((i * 5))), fill="#64A136", width=2)
            # añadir a los pbc
            self.pbv_port4_conections.append(line_id)
        for i in range(5):
            # crear línea vertical
            line_id = canvas.create_line(
                225 + (i * 5), 30,          # x fijo (columna), y inicial
                225 + (i * 5), 125,        # mismo x, y final
                fill="#64A136", width=2
            )
            # añadir a los pbc
            self.pbv_port4_conections.append(line_id)
        for i in range(5):
            # crear linea
            line_id = canvas.create_line((10+3), (105 + (i * 5)), (285), (105 + ((i * 5))), fill="#64A136", width=2)
            # añadir a los pbc
            self.pbv_port5_conections.append(line_id)
        for i in range(5):
            # crear línea vertical
            line_id = canvas.create_line(
                10 + (i * 5), 40,          # x fijo (columna), y inicial
                10 + (i * 5), 125,        # mismo x, y final
                fill="#64A136", width=2
            )
            # añadir a los pbc
            self.pbv_port5_conections.append(line_id)
        for i in range(5):
            # crear línea vertical
            line_id = canvas.create_line(
                70 + (i * 5), 40,          # x fijo (columna), y inicial
                70 + (i * 5), 80,        # mismo x, y final
                fill="#64A136", width=2
            )
            # añadir a los pbc
            self.pbc_port1_conections.append(line_id)
        for i in range(5):
            # crear línea vertical
            line_id = canvas.create_line(
                115 + (i * 5), 40,          # x fijo (columna), y inicial
                115 + (i * 5), 80,        # mismo x, y final
                fill="#64A136", width=2
            )
            # añadir a los pbc
            self.pbc_port2_conections.append(line_id)
        for i in range(5):
            # crear línea vertical
            line_id = canvas.create_line(
                160 + (i * 5), 40,          # x fijo (columna), y inicial
                160 + (i * 5), 80,        # mismo x, y final
                fill="#64A136", width=2
            )
            # añadir a los pbc
            self.pbc_port3_conections.append(line_id)

        # posiciones
        chip_x, chip_y = 9, 18+5
        # el chip
        chip_w, chip_h = 30, 20

        # La soldadura del mainchip
        canvas.create_rectangle(0,10+5,40,50+5,fill="#2C2C2C")
        # el mainchip
        CPUBox = tk.Canvas(canvas, width=25, height=25, bg="#FF970E", highlightthickness=0)
        # poner el mainchip
        CPUBox.place(x=chip_x, y=chip_y)
        # que ejecuta codigo
        CPUBox.bind("<Button-1>", lambda e: self.excode())

        # posicion de x
        chip_x -= 3
        # Dibujar patitas arriba
        for i in range(2, chip_w, 7):
            canvas.create_rectangle(chip_x+i, (chip_y-5), chip_x+i+5, (chip_y), fill="#C67914")
        chip_y += 29
        for i in range(2, chip_w, 7):
            canvas.create_rectangle(chip_x+i, (chip_y-5), chip_x+i+5, (chip_y), fill="#C67914")
        chip_y -= 29
        chip_x += 3
        for i in range(2, chip_h, 7):
            canvas.create_rectangle((chip_x+chip_w)-5, (chip_y+i), (chip_x+chip_w+5)-5, (chip_y+i+5), fill="#C67914")
        chip_x -= 31
        for i in range(2, chip_h, 7):
            canvas.create_rectangle((chip_x+chip_w)-5, (chip_y+i), (chip_x+chip_w+5)-5, (chip_y+i+5), fill="#C67914")

        # soldadura del puerbo usb-c
        canvas.create_rectangle(185-10,14,220,46,fill="#2C2C2C")
        # El puerto USB-C
        USBCPush = tk.Canvas(canvas, width=25, height=25, bg="#C7C7C7", highlightthickness=0)
        # poner el usbc
        USBCPush.place(x=185, y=18)
        # que carga una imagen usb
        USBCPush.bind("<Button-1>", lambda e: self.load_usb_image())

        chip_x = 180

        # partes del usb
        canvas.create_rectangle(chip_x,20,chip_x+5,40,fill="#BBBBBB")
        canvas.create_rectangle(chip_x+29,20,chip_x+29+5,40,fill="#BBBBBB")

        # el boton para encender
        PowerOnButton = tk.Canvas(canvas, width=25, height=25, bg="#C7C7C7", highlightthickness=0)
        # posicion x
        chip_x = 265
        # posicion y
        chip_y = 126
        # enciende la pc
        PowerOnButton.bind("<Button-1>", lambda e: self._pc_on_())
        # ponerlo en la posicion
        PowerOnButton.place(x=270, y=103)
        # las cosas
        canvas.create_rectangle(chip_x,chip_y-20,chip_x+5,chip_y,fill="#BBBBBB")
        canvas.create_rectangle(chip_x+29,chip_y-20,chip_x+29+5,chip_y,fill="#BBBBBB")
        # la bateria
        BateryPush = tk.Canvas(canvas, width=50, height=25, bg="#A9E34C", highlightthickness=0)
        # ponerlo en la posicion
        BateryPush.place(x=250, y=15)
        
        self.ports = []

        # hacer los placeholders
        for i in range(3):
            chip_x = 60 + (i * 50)
            # soldadura
            canvas.create_rectangle(chip_x-7, 67,(chip_x-10)+40, 67+30,fill="#2C2C2C")
            
            # partes del placeholder
            canvas.create_rectangle(chip_x-5, 72,(chip_x-5)+5, 72+20,fill="#BBBBBB")
            canvas.create_rectangle((chip_x-5)+29, 72,(chip_x-5)+29+5, 72+20,fill="#BBBBBB")

            # el puerto
            PortPush = tk.Canvas(canvas, width=25, height=25, bg="#C7C7C7", highlightthickness=0)
            # como un boton
            PortPush.bind("<Button-1>", lambda e, idx=i: self.conect_hardware(1+idx))
            # ponerlo en x y y
            PortPush.place(x=chip_x, y=70)
            # agregarlo a los puertos
            self.ports.append(PortPush)
            e4app_tooltip(PortPush, "port_slot" + str(i) + " : click para cargar un dispositivo")

        # Si cierras la ventana principal → cerrar todo
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_todo)

        # Placeholder para la segunda ventana
        self.output_win = None

        self.root.bind("<Key>", self.on_key)

        e4app_tooltip(CPUBox, "main chip (click para ejecutar comando)")
        e4app_tooltip(BateryPush, "bateria")
        e4app_tooltip(USBCPush, "puerto usb (click para seleccionar una imagen de usb)")
        e4app_tooltip(PowerOnButton, "boton de encendido (click para encender el dispositivo)")


        threading.Thread(target=self.prompt_loop, daemon=True).start()
        self.update_devices_loop()
    # el loop
    def prompt_loop(self):
        while True:
            # codigo
            code_asm = input("> ")

            if (code_asm != ""):
                # codigo
                code = e4asm.assamble_code(code_asm)
                program = list(code)
                print(program)
                
                old_pc = self.VirtualMachine.pc
                self.VirtualMachine.pc = 0
                while self.VirtualMachine.pc < len(program):
                    self.VirtualMachine.step(program)
                self.VirtualMachine.pc = old_pc
    # inicializar menu
    def menu_init(self, rt, donly=False):
        # barra de menu
        menubar = tk.Menu(rt, tearoff=0)
        # la barra de menu de hardware
        hardware_menu = tk.Menu(menubar, tearoff=0)
        # el menu de herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        # el menu de poder
        machine_menu = tk.Menu(menubar, tearoff=0)

        # remover un hardware
        remover_hardware = tk.Menu(menubar, tearoff=0)
        # añadir el menu de remover hardware
        hardware_menu.add_cascade(label="Remover", menu=remover_hardware)
        # comando de adaptador de video
        tools_menu.add_command(label="Adaptador de video",command=self.crear_output)
        # comando de abrir codigo
        tools_menu.add_command(label="Abrir codigo",command=self.waitfile)
        # comando de abrir inspector de memoria
        tools_menu.add_command(label="Abrir inspector de memoria",command=self.abrir_debug)
        # para la maquina
        machine_menu.add_command(label="Reiniciar", command=self._pc_reset_)
        # para apagar
        machine_menu.add_command(label="Apagar", command=self.cerrar_todo)
        # menu de remover hardware
        for i in range(3):
            # el comando de hardware
            remover_hardware.add_command(label=str(i+1),command=lambda idx=i: self.disconect_hardware(1+idx))
        # si hay display only
        if donly == True:
            # añadir
            add_hardware = tk.Menu(menubar, tearoff=0)
            # menu de añadir hardware
            for i in range(3):
                # el comando de hardware
                add_hardware.add_command(label=str(i+1),command=lambda idx=i: self.conect_hardware(1+idx))
            # añadir
            hardware_menu.add_cascade(label="Añadir", menu=add_hardware)    

        # añadir el menu de maquina
        menubar.add_cascade(label="Maquina", menu=machine_menu)
        # añadir el menu de hardware
        menubar.add_cascade(label="Hardware", menu=hardware_menu)
        # añadir el menu de tools
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # configurar la barra de menu
        rt.config(menu=menubar)
    # cargar un usb
    def load_usb_image(self):
        # abrir diálogo para seleccionar archivo .img
        file_path = filedialog.askopenfilename(title="Selecciona imagen del pendrive",filetypes=[("Imagen de disco", "*.img"), ("Todos los archivos", "*.*")])
       # si esta 
        if file_path:
            # abrirlo
            with open(file_path, "rb") as f:
                # leer todo el archivo y guardarlo en usb_buffer
                self.usb_buffer = bytearray(f.read())
            # el index del usb
            self.usb_index = 0 
    # abre el debug
    def abrir_debug(self):
        # abrir el debug
        DebugWindow(self.root, self.VirtualMachine)
    # desconecta el hardware
    def disconect_hardware(self,index):
        # desconecta hardware
        i = index - 1
        # el hardware
        hw = self.hardwares[i]

        # si esta el hardware y no se ha desconectado
        if hw and not (hw.disconnect is None):
            # desconectarlo
            hw.disconnect(self.ports[i])
            # el update es none
            hw.update = None
            # el puerto se vuelve de su color original para simular su extraccion
            self.ports[i].configure(bg="#C7C7C7")
    # ejecutar codigo
    def excode(self):
        # pedir la linea asm
        code_asm = pedir_texto()
        # codigo
        code = e4asm.assamble_code(code_asm)
        program = list(code)
        
        old_pc = self.VirtualMachine.pc
        self.VirtualMachine.pc = 0
        while self.VirtualMachine.pc < len(program):
            self.VirtualMachine.step(program)
        self.VirtualMachine.pc = old_pc
    # hacer animacion pbc
    def pbc(self, port=None):
        if (port == 4):
            return

        # diccionario de puertos → rails
        rails = {
            0: self.pbc_conections,
            1: self.pbc_port1_conections,
            2: self.pbc_port2_conections,
            3: self.pbc_port3_conections,
            5: self.pbv_port4_conections,
            6: self.pbv_port5_conections
        }

        rail = rails.get(port)
        if rail:
            self.pbc_in(rail)
        
        self.pbc_in(self.pbc_conections)
    # hacer pbc
    def pbc_in(self, rail=None):
        # usa rail por defecto si no se pasa nada
        rail = rail or self.pbc_conections
        # arranca la animación directamente
        self._pbc_in_(0, False, rail)
    # para in
    def _pbc_in_(self, step=0, restoring=False, rail=None):
        if rail is None:
            rail = self.pbc_conections

        if not restoring:
            if step < len(rail):
                self.canvas.itemconfig(rail[step], fill=self.passing_energy_pbc_color)
                self.canvas.after(10, lambda: self._pbc_in_(step+1, False, rail))
            else:
                self.canvas.after(250, lambda: self._pbc_in_(0, True, rail))
        else:
            if step < len(rail):
                self.canvas.itemconfig(rail[step], fill=self.original_pbc_color)
                self.canvas.after(10, lambda: self._pbc_in_(step+1, True, rail))
    # only display
    def only_display(self):
        # si no se dibuja
        self.root.withdraw()
        # abrir display
        self.crear_output()
        # al cerrarlo, cerrar todo
        self.output_win.protocol("WM_DELETE_WINDOW", self.cerrar_todo)
        # abrir menu
        self.menu_init(self.output_win, True)
    # enciende la pc
    def _pc_on_(self):
        self.pbc(5)
        self.pbc(6)

        cwd = os.getcwd()
        firmware_code = open(self.fd_file, "r").read()
        code_fd = e4asm.assamble_code(firmware_code)
        code = list(code_fd)
        open(os.path.join(cwd, "e4lib", "e4bins", "firmware.o"), "wb").write(code_fd)
        self.VirtualMachine.pc = 0
        self.start(code)
    # para esperar a ejecutar un archivo
    def waitfile(self):
        fl = filedialog.askopenfilename(
            title="Selecciona un archivo",
            filetypes=(("programas objetos", "*.o"), ("Todos los archivos", "*.*"))
        )
        
        program = list(open(fl,"rb").read())

        self.VirtualMachine.pc = 0
        self.start(program)
    # inicio
    def start(self, program):
        self.running = True
        self.pcstop = 0
        self.step(program)
    # fin
    def stop(self):
        self.running = False
    # paso del programa
    def step(self, program):
        if self.VirtualMachine.pc < len(program): 
            for _ in range(100):  # ejecuta 100 instrucciones por ciclo
                self.current_program = program
                if self.VirtualMachine.pc >= len(program):
                    break
                # si esta en halt y las interrupciones estan activadas
                if self.VirtualMachine.in_halt_mode and self.VirtualMachine.mem[0xac01] == 1:
                    # si una tecla viene en camino, atraparla
                    if self.keyboard_comming == True:
                        # ya no hay teclas en camino
                        self.keyboard_comming = False
                        # activar la flag para despertarlo el siguiente ciclo
                        self.VirtualMachine.mem[0xac00] = 1
                        # la interrupcion que fue, 1=teclado
                        self.VirtualMachine.reg['f'] = 1
                        # despertar
                        self.VirtualMachine.in_halt_mode = False
                self.VirtualMachine.step(program)
            # si detener
            if self.running:
                # detener
                self.canvas.after(1, lambda: self.step(program))
            self.pcstop = 1
    # para reiniciar
    def _pc_reset_(self):
        # detener ejecución
        self.stop()

        # limpiar framebuffer de texto (80x25 caracteres, 2 bytes cada uno)
        start = e4hardware_vga.vga_offset
        end   = start + (80 * 25 * 2)

        # opción 1: bucle
        for i in range(start, end):
            self.VirtualMachine.mem[i] = 0

        # opción 2: asignación por slice
        self.VirtualMachine.mem[start:end] = [0] * (end - start)

        # reiniciar después de un pequeño delay
        self.root.after(10, self._pc_on_)
    # crea la ventana de outpud
    def crear_output(self):
        if self.output_win is None or not tk.Toplevel.winfo_exists(self.output_win):
            self.output_win = tk.Toplevel(self.root)
            self.output_win.title("e4sim - display outpud")
            self.output_win.geometry("" + str(8*80) + "x" + str(16*25))

            self.vidmem = tk.Canvas(self.output_win, width=(8*80), height=(16*25), bg="black")
            self.vidmem.pack()

            # Llamar al refresco periódico
            self.actualizar_video()
    # actualizar hardwares
    def upload_devices(self):
        for port, hw in enumerate(self.hardwares):
            if hw and not (hw.update is None):
                hw.update(self.ports[port], self.VirtualMachine.mem)
    # cargar hardware
    def conect_hardware(self, index: int):
        fl = filedialog.askopenfilename(
            title="Selecciona un archivo",
            filetypes=(("codigo python", "*.py"), ("Todos los archivos", "*.*"))
        )
        self.load_hardware(self.ports[index - 1], index-1, open(fl,"rb").read())
    # cargar hardware virutal
    def load_hardware(self, Place: tk.Button, id: int, hardware_code: str):
        namespace = {"__builtins__": __builtins__}
        exec(hardware_code, namespace)

        # inicializar hardware
        if "open" in namespace:
            namespace["open"](Place)

        # asignar callbacks
        self.hardwares[id].update = namespace.get("update")
        self.hardwares[id].disconnect = namespace.get("disconect")
        self.hardwares[id].input = namespace.get("hardware_in")
        self.hardwares[id].outpud = namespace.get("hardware_out")
        for port, hw in enumerate(self.hardwares):
            if hw and hw.update:
                hw.update(self.ports[port], self.VirtualMachine.mem)  # ejemplo de RAM
    # hacerlo
    def update_devices_loop(self):
        # actualizar todos los dispositivos
        self.upload_devices()
        # volver a llamar después de 100 ms
        self.root.after(100, self.update_devices_loop)
    # actualiza el video
    def actualizar_video(self):
        self.vidmem.delete("all")  # limpiar pantalla

        cols, rows = 80, 25
        cell_w, cell_h = 8, 16

        gop_mode = False

        # modo grafico
        if self.VirtualMachine.mem[vga_offset-1] == 1:
            # activar
            gop_mode = True
            # r/c
            cols = cols * cell_w
            rows = rows * cell_h
            # celdas
            cell_h = 1
            cell_h = 1
        for row in range(rows):
            for col in range(cols):
                addr = vga_offset + (row*cols + col)
                pixel_val = self.VirtualMachine.mem[addr]

                if gop_mode:
                    # modo gráfico: cada byte = color
                    color = color_console(pixel_val & 0x0F)
                    self.vidmem.create_rectangle(
                        col, row, col+1, row+1,
                        outline=color, fill=color
                    )
                else:
                    addr = vga_offset + (row*cols + col)*2
                    char_code = self.VirtualMachine.mem[addr]
                    attr = self.VirtualMachine.mem[addr+1]

                    fg = "white"
                    if attr == 0x07:
                        fg = "lightgreen"

                    #fg = color_console(attr & 0x0F)          # color de texto
                    bg = color_console((attr >> 4) & 0x0F)   # color de fondo

                    self.vidmem.create_text(
                        col*cell_w + 4, row*cell_h + 8,
                        text=chr(char_code),
                        fill=fg,
                        font=("Consolas", 10)
                    )

        # Volver a llamar después de 100 ms
        self.vidmem.after(100, self.actualizar_video)
    # cierra todo
    def cerrar_todo(self):
        # Destruye ambas ventanas
        if self.output_win is not None and tk.Toplevel.winfo_exists(self.output_win):
            self.output_win.destroy()
        self.root.destroy()
    # para enviar datos a un dispositivo
    def _io_outpud_(self, port:int, data:int):
        # puerto 0
        if (port == 0): 
            return

        # resetear lector de usb
        if (port == 0x30):
            # indice es 0
            self.usb_index = 0
            return
        
        # setear el indice de la usb
        if (port == 0x32):
            # setear
            self.usb_index = data
            return
        
        # vaciar el buffer de programa externo a ejecutar
        if (port == 0x40):
            # arrays
            self.program_buffer = bytearray()
            # indice del programa
            self.program_index = 0
            return
        
        # el puerto para mandar un byte al buffer de programa
        if (port == 0x41):
            # el buffer
            self.program_buffer.append(data)
            # siguiente entrada
            self.program_index += 1
            return
        
        # para ejecutar el codigo del programa
        if port == 0x42:
            # el pc antiguo
            old_pc = self.VirtualMachine.pc
            # programa antiguo
            old_program = self.current_program
            # funcion
            def worker():
                # copiar
                program = self.program_buffer[:]
                # buffer actual
                self.current_program = self.program_buffer
                # pc=0
                self.VirtualMachine.pc = 0
                # ejecutar programa
                while self.VirtualMachine.pc < len(program) and not self.VirtualMachine.in_halt_mode:
                    # si no se ejecuta
                    if self.running == False:
                        break
                    # si manda iret
                    if self.VirtualMachine.exit_program:
                        # salir
                        self.VirtualMachine.exit_program = False
                        break
                    # siguiente instruccion
                    self.VirtualMachine.step(program)
                # restaurar el program buffer
                self.current_program = old_program

            # arbol a ejecutar
            t = threading.Thread(target=worker)
            # iniciar
            t.start()
            # esperar a que termine
            t.join()

            # recuperar el program counter
            self.VirtualMachine.pc = old_pc
            return
        
        # obtener el programa actual
        if port == 0x50:
            # El valor escrito al puerto es la dirección base
            base_addr = data
            # el address
            prog = self.current_program
            # setearlo
            for i, byte in enumerate(prog):
                # la base
                if base_addr + i < len(self.VirtualMachine.mem):
                    # setear memoria
                    self.VirtualMachine.mem[base_addr + i] = byte
            # setear base
            self.idt_table_base = base_addr
            return
        
        # setear el indice de idt a modificar
        if port == 0x51:
            # setear
            self.current_idt_index = data
            return
        
        # modificar offset de idt
        if port == 0x52:
            # si no esta
            if self.offsets_idt.get(self.current_idt_index) is None:
                # crearlo
                self.offsets_idt.__setitem__(self.current_idt_index, data)
            # ajustarlo
            self.offsets_idt[self.current_idt_index] = data 
            return
        
        # funcion interna para llamar interrupciones
        if (port == 0x53):
            # el tamaño maximo
            size_max = self.current_idt_size
            # inicio
            start = self.idt_table_base
            # fin
            end = (self.idt_table_base)+size_max
            # la interrupcion
            interruption = self.VirtualMachine.mem[start:end]

            # guardar pc
            old_pc = self.VirtualMachine.pc
            # funcion
            def worker():
                # el pc es el offset en los id
                self.VirtualMachine.pc = self.offsets_idt[data]
                # ejecutar programa
                while self.VirtualMachine.pc < len(interruption) and not self.VirtualMachine.in_halt_mode:
                    # si no se ejecuta
                    if self.running == False:
                        return
                    # si sale
                    if self.VirtualMachine.exit_program:
                        # salir
                        self.VirtualMachine.exit_program = False
                        # cargar antiguo program counter
                        self.VirtualMachine.pc = old_pc
                        break
                    # siguiente instruccion
                    self.VirtualMachine.step(interruption)

            # el proceso
            t = threading.Thread(target=worker)
            # iniciar
            t.start()
            # esperar a que termine
            t.join()

            # pc anterior
            self.VirtualMachine.pc = old_pc
            return
        
        # setear el tamaño del idt
        if (port == 0x54):
            # setearlo
            self.current_idt_size = data
            return
        
        # red
        if (port == 0x60):
            self.net.lan_send(data)
            return

        # simular energia pasando por los circuitos pbc
        self.pbc(port=port)

        # puerto de vga
        if (port == 4):
            # añadir dato
            self.VirtualMachine.mem[vga_offset + self.vidoff] = data
            # siguiente casilla
            self.vidoff = self.vidoff + 1
        # si la funcion de outpud existe
        elif not (self.hardwares[port-1].outpud is None):
            # mandar
            self.hardwares[port-1].outpud(self.ports[port-1], data)
        else:
            # no se llamo
            print("e4sim: cant find the hardware in that place")
    # para recibir datos de un dispositivo
    def _io_input_(self, port:int) -> int:
        # puerto 0
        if (port == 0): return 0

        # puerto para recibir una dato de la usb
        if port == 0x31:
            # si la imagen tiene longitud 0
            if len(self.usb_buffer) == 0: return 0
            # si el index es mayor a la longitud
            if self.usb_index >= len(self.usb_buffer): return 0

            # obtener el dato de la usb
            val = self.usb_buffer[self.usb_index]
            # sumar indice para lectura continua
            self.usb_index += 1

            # retornar dato
            return val
        
        # puerto para obtener el usb index
        if port == 0x32:
            return self.usb_index

        # puerto para obtener la longitud del programa actual
        if port == 0x55: return self.current_program.__len__()

        # para leer una tecla
        elif (port == 0x20): return key_queue.get()

        # leer
        elif (port == 0x60): return self.net.lan_recive()

        # hace la animacion como si estuviese cruzando energia por los circuitos
        self.pbc(port=port)

        # retorna el dato
        return self.hardwares[port-1].input(self.ports[port-1])
    # tecla
    def on_key(self, event):
        # Guardar la tecla en la cola
        key_queue.put(event.char)
        self.keyboard_comming = True

def main():
    # Ejecutar la app
    app = Erick4004SimuApp()

    # parametros
    parameters = argv[1:]

    initialize_auto = False
    param_index = 0
    while param_index < len(parameters):
        # parametro
        param = parameters[param_index]
        # insertar usb manualmente
        if param == "-usb":
            # tiene que ser un .img
            usb_path = parameters[param_index + 1]
            # abrir
            app.usb_buffer = open(usb_path, "rb").read()
            # aumentar
            param_index += 1
            # avisar
            print("image '" + usb_path + "' loaded as the usb virtual usb pendrive")
        # si es baremetal
        elif param == "-baremetal":
            app.fd_file = os.path.join(os.getcwd(), "e4lib", "firmware", "baremetal.asm")
        # si es autopower
        elif param == "-autopower":
            # encenderlo
            initialize_auto = True
        # kernel para el sistema
        elif param == "-kernel":
            # el archivo
            kernel_file = parameters[param_index + 1]
            # el filesystem
            fs = filesystem.new_partition(open(kernel_file, "rb").read())
            # ponerlo
            app.usb_buffer = fs
            # sumar
            param_index += 1
        # solo display
        elif param == "-onlydisplay":
            # solo display
            app.only_display()
        param_index += 1

    # si se inicializa
    if initialize_auto:
        def auto_power_on():
            # presionar el botón de encendido automáticamente
            app._pc_on_()
        # lanzar en otro hilo
        threading.Thread(target=auto_power_on, daemon=True).start()

    app.root.mainloop()

main()