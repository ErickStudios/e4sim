# arboles
import threading
# tiempo
import time
# importar la mdt
from e4lib.e4arch.protected.mdt import e4arch_MDTEntry
# importar excepciones
from e4lib.e4arch.protected.exceptions import e4arch_exception
# la maquina virtual
class e4arch:
    # inicializa
    def __init__(self, mem_size=4194304):
        # memoria
        self.mem = bytearray(mem_size)
        # flagoff
        self.flagoff = False
        # registros
        self.reg = { 'a':0, 'b':0, 'c':0, 'd':0, 'e':0, 'f':0, 'ds':0, 'off':0,'cycl':0,'sp':mem_size-80}
        # program counter
        self.pc = 0
        # banderas
        self.flags = {'Zero':False,'Greater':False,'Less':False}
        # si hace iret
        self.exit_program = False
        # la pc
        self.pc_fetch = None
        # en halt mode
        self.in_halt_mode = False
        # compuerta protejido, arranca en modo 'base'
        self.protect_no_base_mode = False
        # ah?
        self.know_know = 0
        # crear los eventos
        threading.Thread(target=self._extern_events_).start()
    # eventos externos
    def _extern_events_(self):
        # ejecutar
        while True:
            if self.flagoff:
                return

            # funciones de modo base
            if not self.protect_no_base_mode:
                pass
            # funciones si esta en modo protejido
            if self.protect_no_base_mode:
                # si esta recien empezando crear
                if not hasattr(self, "mdt_vector"): self.mdt_vector:dict[int, e4arch_MDTEntry] = dict()
                if not hasattr(self, "mdt_entry_set"): self.mdt_entry_set:int = int()
                if not hasattr(self, "protected_ring3"): self.protected_ring3:bool = bool()
            # dormir
            time.sleep(2)
    # obtener
    def fetch(self, program):
        # obtener instruccion
        op = program[self.pc]; self.pc += 1
        # retornarlo
        return op
    # lee un byte
    def read_byte(self, program):
        # obtenerlo
        b = program[self.pc]; self.pc += 1
        # retornarlo
        return b
    # lee un u32
    def read_u32_be(self, program):
        # obtenerlo
        v = (program[self.pc]<<24)|(program[self.pc+1]<<16)|(program[self.pc+2]<<8)|program[self.pc+3]
        # siguiente
        self.pc += 4
        # retornarlo
        return v
    # paso
    def step(self, program):
        # direccion de hlt
        hlt_no_direction = 0xac00
        # interrupciones flag
        interruption_flag_direction = 0xac01

        # que 💀
        mck = False

        # hacerlo
        if self.in_halt_mode:
            # revisar si hay interrupción pendiente y habilitada
            if self.mem[hlt_no_direction] == 1 and self.mem[interruption_flag_direction] == 1:
                self.mem[hlt_no_direction] = 0
                self.in_halt_mode = False
            else:
                return

        # operacion
        op = self.fetch(program)
        if op == 0x01:  # mov dst,src (nibbles)
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            self._set_reg(dst, self._get_reg(src))

            # --firmware: ah?
            if dst == 0x7 and src == 0x7 and self.know_know == 1: mck = True

        elif op == 0x02:  # ivar size addr
            size = self.read_byte(program)
            addr = self.read_u32_be(program)

            # Setear DS al inicio de la variable
            self.reg['ds'] = addr
        elif op == 0x03:  # align n (define: reset off)
            n = self.read_byte(program)
            self.reg['off'] = n

        elif op == 0x04:  # pub value
            val = self.read_byte(program)
            addr = self.reg['ds'] + self.reg['off']
            if 0 <= addr < len(self.mem):
                self.mem[addr] = val & 0xFF
            self.reg['off'] += 1

        elif op == 0x05:  # push reg (i32)
            reg_code = self.read_byte(program)
            val = self._get_reg(reg_code) & 0xFFFFFFFF  # asegurar 32 bits
            # reservar 4 bytes en la pila
            self.reg['sp'] -= 4
            # escribir en memoria en orden little-endian
            self.mem[self.reg['sp']]     = (val >> 0) & 0xFF
            self.mem[self.reg['sp'] + 1] = (val >> 8) & 0xFF
            self.mem[self.reg['sp'] + 2] = (val >> 16) & 0xFF
            self.mem[self.reg['sp'] + 3] = (val >> 24) & 0xFF

            # --firmware: que? 💀
            if reg_code == 0x8 and self.know_know == 0: mck = True

            # --firmware: q?
            if reg_code == 0x1 and self.know_know == 2: mck = True

        elif op == 0x06:  # pop reg (i32)
            reg_code = self.read_byte(program)
            # leer 4 bytes en orden little-endian
            val = (
                self.mem[self.reg['sp']] |
                (self.mem[self.reg['sp'] + 1] << 8) |
                (self.mem[self.reg['sp'] + 2] << 16) |
                (self.mem[self.reg['sp'] + 3] << 24)
            )
            self._set_reg(reg_code, val)
            self.reg['sp'] += 4
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

        elif op == 0x0E:  # out port,reg
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF

            self._io_out_(dst, src)

        elif op == 0x0F:  # gub reg
            register = self.read_byte(program)
            self._set_reg(register, self.mem[self.reg["ds"] + self.reg["off"]])
            self.reg['off'] += 1
            # --firmware: q?
            if register == 0x1 and self.know_know == 3: mck = True

        elif op == 0x10: # dbg reg
            register = self.read_byte(program)
            print(self._get_reg(register))

        elif op == 0x11: #hlt
            self.in_halt_mode = True
        elif op == 0x12: #sti
            self.mem[interruption_flag_direction] = 1
        elif op == 0x13: #cli
            self.mem[interruption_flag_direction] = 0
        elif op == 0x14: # pubr = pub with register
            val = self.read_byte(program)
            addr = self.reg['ds'] + self.reg['off']
            if 0 <= addr < len(self.mem):
                self.mem[addr] = self._get_reg(val)
            self.reg['off'] += 1

            # --firmware: noo,me van a matar causa
            if val == 0x1 and self.know_know == 5: mck = True

        elif op == 0x15:  # pul = put long (32 bits)
            val = self.read_u32_be(program)              # lee un entero de 32 bits
            addr = self.reg['ds'] + self.reg['off']      # calcula dirección base

            if 0 <= addr <= len(self.mem) - 4:           # asegúrate de que hay espacio
                # descomponer en 4 bytes big-endian
                self.mem[addr]     = (val >> 24) & 0xFF
                self.mem[addr + 1] = (val >> 16) & 0xFF
                self.mem[addr + 2] = (val >> 8)  & 0xFF
                self.mem[addr + 3] = val & 0xFF

            self.reg['off'] += 4                          # avanzas 4 posiciones
        elif op == 0x16:  # gul = get long (32 bits)
            register = self.read_byte(program)              # a qué registro cargar
            addr = self.reg['ds'] + self.reg['off']         # dirección base

            if 0 <= addr <= len(self.mem):              # asegurar que hay 4 bytes
                # reconstruir el entero desde 4 bytes big-endian
                val = (
                    (self.mem[addr] << 24) |
                    (self.mem[addr + 1] << 16) |
                    (self.mem[addr + 2] << 8) |
                    self.mem[addr + 3]
                )
                self._set_reg(register, val)                # guardar en el registro

            self.reg['off'] += 4                            # avanzar 4 posiciones
        elif op == 0x17:  # loop addr
            # --firmware: este es mi fin
            if self.know_know == 7: mck = True

            addr = self.read_u32_be(program)   # dirección del bloque
            if self.reg['cycl'] > 0:
                self.reg['cycl'] -= 1
                self.pc = addr                 # saltar al inicio del loop
            else:
                pass
        elif op == 0x18:  # cmp reg1, reg2
            operand = self.read_byte(program)
            reg1 = operand & 0xF
            reg2 = (operand >> 4) & 0xF
            val1 = self._get_reg(reg1)
            val2 = self._get_reg(reg2)

            self.flags['Zero'] = (val1 == val2)
            self.flags['Greater'] = (val1 > val2)
            self.flags['Less'] = (val1 < val2)

        elif op == 0x19:  # cq addr
            addr = self.read_u32_be(program)
            if self.flags['Zero']:
                ret = self.pc
                self.reg['sp'] -= 4
                self.mem[self.reg['sp']:self.reg['sp']+4] = ret.to_bytes(4, "big")
                self.pc = addr

        elif op == 0x1A:  # cnq addr
            addr = self.read_u32_be(program)
            if not self.flags['Zero']:
                ret = self.pc
                self.reg['sp'] -= 4
                self.mem[self.reg['sp']:self.reg['sp']+4] = ret.to_bytes(4, "big")
                self.pc = addr

        elif op == 0x1B:  # cg addr
            addr = self.read_u32_be(program)
            if self.flags['Greater']:
                ret = self.pc
                self.reg['sp'] -= 4
                self.mem[self.reg['sp']:self.reg['sp']+4] = ret.to_bytes(4, "big")
                self.pc = addr

        elif op == 0x1C:  # cng addr
            addr = self.read_u32_be(program)
            if not self.flags['Greater']:
                ret = self.pc
                self.reg['sp'] -= 4
                self.mem[self.reg['sp']:self.reg['sp']+4] = ret.to_bytes(4, "big")
                self.pc = addr
        elif op == 0x1D:  # mov src
            reg = self.read_byte(program)              # lee el registo
            val = self._get_reg(reg)                    # lee el valor
            addr = self.reg['ds'] + self.reg['off']      # calcula dirección base

            if 0 <= addr <= len(self.mem) - 4:           # asegúrate de que hay espacio
                # descomponer en 4 bytes big-endian
                self.mem[addr]     = (val >> 24) & 0xFF
                self.mem[addr + 1] = (val >> 16) & 0xFF
                self.mem[addr + 2] = (val >> 8)  & 0xFF
                self.mem[addr + 3] = val & 0xFF

            self.reg['off'] += 4                          # avanzas 4 posiciones
        elif op == 0x1E: # inc
            reg = self.read_byte(program)

            self._set_reg(reg, self._get_reg(reg) + 1)
            # --firmware: pipipi
            if reg == 0x8 and self.know_know == 6: mck = True

        elif op == 0x1F: # dec
            reg = self.read_byte(program)
            self._set_reg(reg, self._get_reg(reg) - 1)

            # --firmware: a huevo... espera que
            if reg == 0xA and self.know_know == 4: mck = True

        elif op == 0x20: # int
            reg = self.read_byte(program)
            interruption = self._get_reg(reg)
            self.pc_fetch._io_outpud_(0x53, interruption)
        elif op == 0x21: # exit
            self.exit_program = True
        elif op == 0x22:  # shl dst,src
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            # desplazamiento lógico a la izquierda
            val = self._get_reg(dst) << self._get_reg(src)
            self._set_reg(dst, val & 0xFFFFFFFF)  # limitar a 32 bits

        elif op == 0x23:  # shr dst,src
            operand = self.read_byte(program)
            dst = (operand >> 4) & 0xF
            src = operand & 0xF
            # desplazamiento lógico a la derecha
            val = (self._get_reg(dst) & 0xFFFFFFFF) >> self._get_reg(src)
            self._set_reg(dst, val)
        else:
            pass

        if not self.protect_no_base_mode:
            if mck == True:
                print("e4arch_32: Level Up is coming, don't ruin it.")
                self.know_know += 1
            else:
                if (self.know_know != 0): print("e4arch_32: You were close, very close, but it was ruined; the firmware survives one more day.")
                self.know_know = 0

            if self.know_know == 8 and mck == True:
                print("e4arch_32: protecte mode actived")
                self.protect_no_base_mode = True
                self.know_know = 0
    # manda algo al puerto
    def send_device(self, puerto, dato):
        # modificar el mdt_entry_set
        if puerto == 0x3DD:
            self.mdt_entry_set = dato
            return
        
        # modificar una entrada
        if puerto == 0x3DE:
            # lanzar un not ready exception
            if (not self.protect_no_base_mode): e4arch_exception("NR")
            # si esta en modo ring3
            if (self.protected_ring3): e4arch_exception("GP")
            # entrada a setear
            self.mdt_vector[self.mdt_entry_set] = e4arch_MDTEntry.from_memory(mem=self.mem, offset=dato)
            return

        self.pc_fetch._io_outpud_(puerto, dato)
    # recibe algo de un puerto
    def recive_device(self, puerto):
        if (puerto == 0x3DD):
            return self.mdt_entry_set

        return self.pc_fetch._io_input_(puerto)
    # obtiene un registro
    def _get_reg(self, code):
        # mapa inverso según registers
        table = {1:'a',2:'b',3:'c',4:'d',5:'e',6:'f',7:'ds', 8:'cycl', 9:'sp', 10:'off'}
        # nombre
        name = table.get(code)
        # retornarlo
        return self.reg[name] if name else 0
    # hacer ind
    def _io_in_(self, reg1a, reg2a):
        # registro 1
        reg1 = self._get_reg(reg1a)
        # registro 2
        reg2 = self._get_reg(reg2a)
        # datos
        data = self.recive_device(reg1)
        # enviar dato
        self._set_reg(reg2a, data)
    # hacer out
    def _io_out_(self, reg1a, reg2a):
        # registro 1
        reg1 = self._get_reg(reg1a)
        # registro 2
        reg2 = self._get_reg(reg2a)
        # enviar dato
        self.send_device(reg1, reg2)
    # setear registro
    def _set_reg(self, code, value):
        table = {1:'a',2:'b',3:'c',4:'d',5:'e',6:'f',7:'ds', 8:'cycl', 9:'sp', 10:'off'}
        name = table.get(code)
        if name: self.reg[name] = value
#@alias
e4arch_32 = e4arch
#@alias
e4arch_32bit = e4arch