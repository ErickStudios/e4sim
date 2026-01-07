registers = {
    "a": 0x1,
    "b": 0x2,
    "c": 0x3,
    "d": 0x4,
    "e": 0x5,
    "f": 0x6,
    "ds": 0x7,
    "cycl": 0x8,
    "sp":0x9,
    "off":0xA
}

class AssemblerContext:
    def __init__(self):
        # Diccionario de símbolos: nombre -> dirección
        self.symbols = {}
        # Puntero actual del segmento de datos (ds)
        self.ds_pointer = 0x00000000

    def add_variable(self, name, size, direction=None):
        if direction is None:
            # Guardar variable en la tabla de símbolos
            self.symbols[name] = self.ds_pointer
            # Avanzar el puntero del segmento de datos
            self.ds_pointer += size
        else:
            self.symbols[name] = direction
        return self.symbols[name]

    def get_address(self, name):
        # Obtener dirección de una variable
        return self.symbols.get(name, None)

def assemble_solve(syntax: str, context: AssemblerContext):
    # Caso: variable declarada con db
    if syntax in context.symbols:
        return context.symbols[syntax]

    # Caso: literal de carácter, ej. 'h'
    if len(syntax) == 3 and syntax[0] == "'" and syntax[-1] == "'":
        return ord(syntax[1])

    # Caso: número decimal
    if syntax.isdigit():
        return int(syntax)

    # Caso: número hexadecimal
    if syntax.startswith("0x"):
        return int(syntax, 16)

    # Caso: registro
    if syntax in registers:
        return registers[syntax]
    
    if syntax == "":
        return "0"

# mover datos
def assemble_mov(dst, src):
    opcode = 0x01
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]

# in
def assemble_in(dst, src):
    opcode = 0x0D
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]

# out
def assemble_out(dst, src):
    opcode = 0x0E
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]

# selecciona la variable a hacer
def assemble_ivar(name, size, direction):
    opcode = 0x02
    size_byte = size & 0xFF
    dir_bytes = list(direction.to_bytes(4, "big"))
    return [opcode, size_byte] + dir_bytes

# resetea off
def assemble_align(nm):
    opcode = 0x03
    operand = nm
    return [opcode, operand]

# pub byte, para poner un byte a una variable a la que apunta ds, y sumarle off, cada vez se hace (ds + off)=byte
def assemble_pub(pub):
    opcode = 0x04
    operand = pub
    return [opcode, operand]

# push
def assemble_push(register):
    opcode = 0x05
    operand = registers[register]
    return [opcode, operand]

# gub
def assemble_gub(register):
    opcode = 0x0F
    operand = registers[register]
    return [opcode, operand]

# dbg
def assemble_dbg(register):
    opcode = 0x10
    operand = registers[register]
    return [opcode, operand]

# pop
def assemble_pop(register):
    opcode = 0x06
    operand = registers[register]
    return [opcode, operand]

def assemble_call(addr: int):
    opcode = 0x7
    dir_bytes = list(addr.to_bytes(4, "big"))
    return [opcode] + dir_bytes

def assemble_add(dst, src):
    opcode = 0x09
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]

def assemble_sub(dst, src):
    opcode = 0x0A
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]

def assemble_mul(dst, src):
    opcode = 0x0B
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]

def assemble_div(dst, src):
    opcode = 0x0C
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]

def assemble_ret():
    opcode = 0x8
    return [opcode]

def assemble_line(line, context:AssemblerContext, len:int):
    line = line.split(";")[0].strip()
    if not line:
        return []

    parts = line.split()
    instr = parts[0].lower()

    if instr == "label":
        context.symbols
        name = parts[1].split(",")[0]

        context.symbols[name] = len

        return []

    elif instr == "mov":
        dst, src = parts[1].split(",")
        return assemble_mov(dst, src)
    
    elif instr == "in":
        dst, src = parts[1].split(",")
        return assemble_in(dst, src)
    
    elif instr == "gub":
        reg = parts[1]
        return assemble_gub(reg)

    elif instr == "out":
        dst, src = parts[1].split(",")
        return assemble_out(dst, src)

    elif instr == "ivar":
        name, rest = parts[1].split(",")
        size = int(rest)

        # Ya debe estar declarada con db
        ptr = int(assemble_solve(name, context))
        if ptr is None:
            raise ValueError(f"Variable {name} no declarada con db")

        # Generar bytes de la instrucción ivar
        return assemble_ivar(name, size, ptr)

    elif instr == "align":
        ps = (parts[1].split(","))
        count = int(ps[0])

        return assemble_align(count)

    elif instr == "push":
            reg = parts[1]
            return assemble_push(reg)

    elif instr == "pop":
        reg = parts[1]
        return assemble_pop(reg)
    
    elif instr == "dbg":
        reg = parts[1]
        return assemble_dbg(reg)
    
    elif instr == "call":
        addr = int(assemble_solve(parts[1].split(",")[0], context)) 
        return assemble_call(addr)

    elif instr == "ret":
        return assemble_ret()
    
    elif instr == "pub":
        ps = parts[1].split(",")   # lista de registros o símbolos
        prs = []

        for name in ps:
            name = name.strip()  # quitar espacios
            prs.append(0x04)     # opcode de pub
            prs.append(int(assemble_solve(name, context)))  # resolver nombre

        return prs
    elif instr == "db":
        name, rest, direction = parts[1].split(",")
        size = int(rest)

        # Registrar variable en el contexto
        context.add_variable(name, size)

        return []
    
    elif instr == "add":
        dst, src = parts[1].split(",")
        return assemble_add(dst, src)

    elif instr == "sub":
        dst, src = parts[1].split(",")
        return assemble_sub(dst, src)

    elif instr == "mul":
        dst, src = parts[1].split(",")
        return assemble_mul(dst, src)

    elif instr == "div":
        dst, src = parts[1].split(",")
        return assemble_div(dst, src)

    elif instr == "hlt":
        return [0x11]
    elif instr == "sti":
        return [0x12]
    elif instr == "cli":
        return [0x13]
    else:
        return []
def instr_length(line, context):
    parts = line.split(";")[0].strip().split()
    if not parts:
        return 0
    instr = parts[0].lower()

    if instr == "label":
        return 0
    elif instr == "mov":
        return 2
    elif instr == "in":
        return 2
    elif instr == "out":
        return 2
    elif instr == "add":
        return 2
    elif instr == "gub":
        return 2
    elif instr == "dbg":
        return 2
    elif instr == "sub":
        return 2
    elif instr == "mul":
        return 2
    elif instr == "div":
        return 2
    elif instr == "push":
        return 2
    elif instr == "pop":
        return 2
    elif instr == "call":
        return 5   # opcode + 4 bytes de dirección
    elif instr == "ret":
        return 1
    elif instr == "pub":
        ps = parts[1].split(",")
        return len(ps) * 2   # cada pub = opcode + operando
    elif instr == "ivar":
        return 6   # opcode + size + 4 bytes addr
    elif instr == "align":
        return 2
    elif instr == "db":
        return 0
    elif instr == "cli" or instr == "sti" or instr == "hlt":
        return 1
    else:
        raise ValueError(f"Instrucción desconocida: " + line)
def assamble_code(code:str):
    content = code.replace("\r", "\n").split("\n")
    context = AssemblerContext()

     # Primera pasada: registrar labels
    pc = 0
    for line in content:
        parts = line.split(";")[0].strip().split()
        if not parts:
            continue
        instr = parts[0].lower()
        if instr == "label":
            name = parts[1].split(",")[0]
            context.symbols[name] = pc
        else:
            # calcula tamaño de instrucción para avanzar pc
            pc += instr_length(line, context)

    # Segunda pasada: ensamblar
    program = []
    pc = 0
    for line in content:
        instr_bytes = assemble_line(line, context, pc)
        program += instr_bytes
        pc += len(instr_bytes)

    return bytes(program)
