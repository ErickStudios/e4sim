import tkinter as tk
from tkinter import filedialog
import time
import importlib.util
from tkinter import simpledialog
import e4lib.assambler as e4asm

def pedir_texto():
    # abre el cuadro de diálogo y retorna lo que el usuario escribió
    texto = simpledialog.askstring("Input", "Escribe tu linea de codigo ensamblador")
    return texto

def load_module_from_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ram = [0] * 327432

offset = 0xB82

# tipo de rm
class Hardware:
    def __init__(self, update, disconnect, io_in=None, io_out=None):
        self.update = update
        self.disconnect = disconnect
        self.input = io_in
        self.outpud = io_out
# clase de la VM
class VM:
    def __init__(self, mem_size=65536):
        self.mem = bytearray(mem_size)
        self.reg = { 
            'a':0, 
            'b':0, 
            'c':0, 
            'd':0, 
            'e':0, 
            'f':0, 
            'ds':0, 
            'off':0,
            'cycl':0,
            'sp':122
              }
        self.pc = 0
        self.pc_fetch:Erick4004SimuApp = None
        self.in_halt_mode = False

    def fetch(self, program):
        op = program[self.pc]; self.pc += 1
        return op

    def read_byte(self, program):
        b = program[self.pc]; self.pc += 1
        return b

    def read_u32_be(self, program):
        v = (program[self.pc]<<24)|(program[self.pc+1]<<16)|(program[self.pc+2]<<8)|program[self.pc+3]
        self.pc += 4
        return v

    def step(self, program):
        print(self.pc)
        hlt_no_direction = 0xac00
        interruption_flag_direction = 0xac01

        if self.mem[hlt_no_direction] == 1 and self.in_halt_mode:
            self.in_halt_mode = False

        if self.in_halt_mode:
            return  # no hace nada, CPU detenida

        op = self.fetch(program)
        if op == 0x01:  # mov dst,src (nibbles)
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            self._set_reg(dst, self._get_reg(src))

        elif op == 0x02:  # ivar size addr
            size = self.read_byte(program)
            addr = self.read_u32_be(program)

            # Setear DS al inicio de la variable
            self.reg['ds'] = addr

            # Inicializar memoria
            for i in range(size):
                if addr + i < len(self.mem):
                    self.mem[addr + i] = 0
        elif op == 0x03:  # align n (define: reset off)
            n = self.read_byte(program)
            self.reg['off'] = 0 if n == 0 else (self.reg['off'] % n)

        elif op == 0x04:  # pub value
            val = self.read_byte(program)
            addr = self.reg['ds'] + self.reg['off']
            if 0 <= addr < len(self.mem):
                self.mem[addr] = val & 0xFF
            self.reg['off'] += 1

        elif op == 0x05:  # push reg
            reg_code = self.read_byte(program)
            val = self._get_reg(reg_code)
            self.reg['sp'] -= 1
            self.mem[self.reg['sp']] = val & 0xFF

        elif op == 0x06:  # pop reg
            reg_code = self.read_byte(program)
            val = self.mem[self.reg['sp']]
            self._set_reg(reg_code, val)
            self.reg['sp'] += 1
        elif op == 0x7:  # call addr
            addr = self.read_u32_be(program)
            # push dirección de retorno
            ret = self.pc
            self.reg['sp'] -= 4
            self.mem[self.reg['sp']:self.reg['sp']+4] = ret.to_bytes(4, "big")
            # saltar
            self.pc = addr

        elif op == 0x8:  # ret
            ret = int.from_bytes(self.mem[self.reg['sp']:self.reg['sp']+4], "big")
            self.reg['sp'] += 4
            self.pc = ret
        elif op == 0x11:  # movm dst,addr (opcional)
            dst = self.read_byte(program)
            addr = self.read_u32_be(program)
            self._set_reg(dst, self.mem[addr])

        elif op == 0x09:  # add dst,src
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            self._set_reg(dst, self._get_reg(dst) + self._get_reg(src))

        elif op == 0x0A:  # sub dst,src
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            self._set_reg(dst, self._get_reg(dst) - self._get_reg(src))

        elif op == 0x0B:  # mul dst,src
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            self._set_reg(dst, self._get_reg(dst) * self._get_reg(src))

        elif op == 0x0C:  # div dst,src
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            divisor = self._get_reg(src)
            if divisor != 0:
                self._set_reg(dst, self._get_reg(dst) // divisor)
            else:
                raise ZeroDivisionError("División por cero en VM")
       
        elif op == 0x0D:  # in port,reg
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            self._io_in_(dst, src)

        elif op == 0x0E:  # ouy port,reg
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            self._io_out_(dst, src)

        elif op == 0x0F:  # gub reg
            register = self.read_byte(program)
            self._set_reg(register, self.mem[self.reg["ds"] + self.reg["off"]])

        elif op == 0x10: # dbg reg
            register = self.read_byte(program)
            print(self._get_reg(register))

        elif op == 0x11: #hlt
            self.in_halt_mode = True
        elif op == 0x12: #sti
            self.mem[interruption_flag_direction] = 1
        elif op == 0x13: #cli
            self.mem[interruption_flag_direction] = 1
        else:
            self.pc += 1

    def _get_reg(self, code):
        # mapa inverso según registers
        table = {1:'a',2:'b',3:'c',4:'d',5:'e',6:'f',7:'ds', 8:'cycl', 9:'sp', 10:'off'}
        name = table.get(code)
        return self.reg[name] if name else 0

    def _io_in_(self, reg1a, reg2a):
        reg1 = self._get_reg(reg1a)
        reg2 = self._get_reg(reg2a)
        self.pc_fetch._pbc_in_()
        # enviar dato
        self._set_reg(reg2, self.pc_fetch._io_input_(reg1))
    def _io_out_(self, reg1a, reg2a):
        reg1 = self._get_reg(reg1a)
        reg2 = self._get_reg(reg2a)
        self.pc_fetch._pbc_in_()
        # enviar dato
        self.pc_fetch._io_outpud_(reg1, reg2)
    def _set_reg(self, code, value):
        table = {1:'a',2:'b',3:'c',4:'d',5:'e',6:'f',7:'ds', 8:'cycl', 9:'sp', 10:'off'}
        name = table.get(code)
        if name: self.reg[name] = value & 0xFF
# clase de la aplicacion
class Erick4004SimuApp:
    # inicializar
    def __init__(self):
        self.VirtualMachine = VM()

        self.VirtualMachine.pc_fetch = self

        # Ventana principal: el "computador"
        self.root = tk.Tk()
        self.root.title("e4sim - pc virtual")
        self.root.geometry("370x200")
        self.root.configure(bg="#1E1E1E")

        menubar = tk.Menu(self.root, tearoff=0)
        hardware_menu = tk.Menu(menubar, tearoff=0)
        tools_menu = tk.Menu(menubar, tearoff=0)

        remover_hardware = tk.Menu(menubar, tearoff=0)
        hardware_menu.add_cascade(label="Remover", menu=remover_hardware)
        tools_menu.add_command(label="Adaptador de video",command=self.crear_output)
        tools_menu.add_command(label="Abrir codigo",command=self.waitfile)

        for i in range(3):
            remover_hardware.add_command(
                label=str(i+1),
                command=lambda idx=i: self.disconect_hardware(1+idx)
            )

        menubar.add_cascade(label="Hardware", menu=hardware_menu)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        self.root.config(menu=menubar)

        label0 = tk.Label(self.root, text="\n", background="#1E1E1E", foreground="white")
        label0.pack(pady=0.1)

        canvas = tk.Canvas(self.root, width=220, height=100, bg="#3E6321")
        canvas.pack()

        label1 = tk.Label(self.root, text="Seleccione un componente para modificarlo", background="#1E1E1E", foreground="white")
        label1.pack(pady=0.1)

        self.hardwares = [
            Hardware(lambda place, ram: None, lambda place: None),
            Hardware(lambda place, ram: None, lambda place: None),
            Hardware(lambda place, ram: None, lambda place: None),
        ]
        print("Inicializado hardwares:", self.hardwares)
        self.original_pbc_color = "#64A136"
        self.passing_energy_pbc_color = "#89D44F"

        self.canvas = canvas
        self.pbc_conections = []
        self.pbc_port1_conections = []
        self.pbc_port2_conections = []
        self.pbc_port3_conections = []

        # simulando los circuitos impresos de I/O, para el procesador recibir puertos de la usb, y la usb recibir datos
        # del prosesador
        for i in range(5):
            # crear linea
            line_id = canvas.create_line(3, (10 + (i * 5)), 200, (10 + ((i * 5))), fill="#64A136", width=2)
            self.pbc_conections.append(line_id)

        for i in range(5):
            # crear línea vertical
            line_id = canvas.create_line(
                70 + (i * 5), 30,          # x fijo (columna), y inicial
                70 + (i * 5), 80,        # mismo x, y final
                fill="#64A136", width=2
            )
            self.pbc_port1_conections.append(line_id)

        for i in range(5):
            # crear línea vertical
            line_id = canvas.create_line(
                115 + (i * 5), 30,          # x fijo (columna), y inicial
                115 + (i * 5), 80,        # mismo x, y final
                fill="#64A136", width=2
            )
            self.pbc_port2_conections.append(line_id)

        for i in range(5):
            # crear línea vertical
            line_id = canvas.create_line(
                160 + (i * 5), 30,          # x fijo (columna), y inicial
                160 + (i * 5), 80,        # mismo x, y final
                fill="#64A136", width=2
            )
            self.pbc_port3_conections.append(line_id)

        chip_x, chip_y = 9, 8
        chip_w, chip_h = 30, 20

        # El CPU
        CPUBox = tk.Canvas(canvas, width=25, height=25, bg="#FF970E", highlightthickness=0)
        CPUBox.place(x=chip_x, y=chip_y)
        CPUBox.bind("<Button-1>", lambda e: self.excode())

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

        # El puerto USB-C
        USBCPush = tk.Canvas(canvas, width=25, height=25, bg="#C7C7C7", highlightthickness=0)
        USBCPush.place(x=185, y=8)
        USBCPush.bind("<Button-1>", lambda e: self.waitfile())

        chip_x = 180
        canvas.create_rectangle(
            chip_x,
            10,
            chip_x+5,
            30,
            fill="#BBBBBB"
            )
        canvas.create_rectangle(
            chip_x+29,
            10,
            chip_x+29+5,
            30,
            fill="#BBBBBB"
            )

        # la bateria
        
        BateryPush = tk.Canvas(canvas, width=50, height=25, bg="#A9E34C", highlightthickness=0)
        BateryPush.place(x=5, y=42)
        
        self.ports = []

        # hacer los placeholders
        for i in range(3):
            chip_x = 66 + (i * 45)
            canvas.create_rectangle(
                chip_x-5, 72,
                (chip_x-5)+5, 72+20,
                fill="#BBBBBB"
            )
            canvas.create_rectangle(
                (chip_x-5)+29, 72,
                (chip_x-5)+29+5, 72+20,
                fill="#BBBBBB"
            )
            # capturamos el valor actual de i en una variable local
            
            PortPush = tk.Canvas(canvas, width=25, height=25, bg="#C7C7C7", highlightthickness=0)
            PortPush.bind("<Button-1>", lambda e, idx=i: self.conect_hardware(1+idx))
            PortPush.place(x=chip_x, y=70)

            self.ports.append(PortPush)

        # Si cierras la ventana principal → cerrar todo
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_todo)

        # Placeholder para la segunda ventana
        self.output_win = None

        self.update_devices_loop()
    def disconect_hardware(self,index):
        i = index - 1
        hw = self.hardwares[i]

        if hw and not (hw.disconnect is None):
            hw.disconnect(self.ports[i])
            hw.update = None
            self.ports[i].configure(bg="#C7C7C7")
    # ejecutar codigo
    def excode(self):
        code_asm = pedir_texto()
        code = e4asm.assamble_code(code_asm)
        program = list(code)
        
        self.VirtualMachine.pc = 0
        while self.VirtualMachine.pc < len(program):
            self.VirtualMachine.step(program)
    # hacer animacion pbc
    def pbc(self, port=None):

        # diccionario de puertos → rails
        rails = {
            0: self.pbc_conections,
            1: self.pbc_port1_conections,
            2: self.pbc_port2_conections,
            3: self.pbc_port3_conections,
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
    # para esperar a ejecutar un archivo
    def waitfile(self):
        fl = filedialog.askopenfilename(
            title="Selecciona un archivo",
            filetypes=(("programas objetos", "*.o"), ("Todos los archivos", "*.*"))
        )
        
        program = list(open(fl,"rb").read())

        self.VirtualMachine.pc = 0
        while self.VirtualMachine.pc < len(program):
            self.VirtualMachine.step(program)
    # crea la ventana de outpud
    def crear_output(self):
        if self.output_win is None or not tk.Toplevel.winfo_exists(self.output_win):
            self.output_win = tk.Toplevel(self.root)
            self.output_win.title("Memoria de video 0xB82")
            self.output_win.geometry("640x480")

            self.vidmem = tk.Canvas(self.output_win, width=640, height=480, bg="black")
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

        for row in range(rows):
            for col in range(cols):
                addr = offset + (row*cols + col)*2
                char_code = self.VirtualMachine.mem[addr]
                attr = self.VirtualMachine.mem[addr+1]

                fg = "white"
                if attr == 0x07:
                    fg = "lightgreen"

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
        self.pbc(port=port)
        if (port == 0):
            pass
        if self.hardwares[port-1].outpud:
            self.hardwares[port-1].outpud(self.ports[port-1], data)
        else:
            print("dont call")
    # para recibir datos de un dispositivo
    def _io_input_(self, port:int) -> int:
        self.pbc(port=port)
        if (port == 0):
            return 0
        return self.hardwares[port-1].input(self.ports[port-1])

# Ejecutar la app
app = Erick4004SimuApp()

app.root.mainloop()