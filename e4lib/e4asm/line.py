# registros
from e4lib.e4asm.registers import e4asm_registers as registers
# contexto
from e4lib.e4asm.context import e4asm_context as AssemblerContext
# importar los registros
from e4lib.e4asm.registers import e4asm_registers as registers
# el solve
assemble_solve = AssemblerContext.assemble_solve
# mover datos
def assemble_mov(dst, src=None):
    if src is None: # mov src -> mem[ds+(off+=4)] = src;
        opcode = 0x1D
        operand = (registers[dst])
        return [opcode, operand]
    else:           # mov dst,src -> coppy src val to dst
        opcode = 0x01
        operand = (registers[dst] << 4) | registers[src]
        return [opcode, operand]
# comparar datos
def assemble_cmp(dst, src):
    opcode = 0x18
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
# put long
def assemble_pul(long: int):
    opcode = 0x15
    dir_bytes = list(long.to_bytes(4, "big"))
    return [opcode] + dir_bytes
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
# pubr
def assemble_pubr(pub):
    opcode = 0x14
    operand = pub
    return [opcode, operand]
# inc
def assemble_inc(pub):
    opcode = 0x1E
    operand = registers[pub]
    return [opcode, operand]
# dec
def assemble_dec(pub):
    opcode = 0x1F
    operand = registers[pub]
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
# gul
def assemble_gul(register):
    opcode = 0x16
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
# llamar
def assemble_call(addr: int):
    opcode = 0x7
    dir_bytes = list(addr.to_bytes(4, "big"))
    return [opcode] + dir_bytes
# call equal
def assemble_cq(addr: int):
    opcode = 0x19
    dir_bytes = list(addr.to_bytes(4, "big"))
    return [opcode] + dir_bytes
# call not equal
def assemble_cnq(addr: int):
    opcode = 0x1A
    dir_bytes = list(addr.to_bytes(4, "big"))
    return [opcode] + dir_bytes
# call greater
def assemble_cg(addr: int):
    opcode = 0x1B
    dir_bytes = list(addr.to_bytes(4, "big"))
    return [opcode] + dir_bytes
# call not greater
def assemble_cng(addr: int):
    opcode = 0x1C
    dir_bytes = list(addr.to_bytes(4, "big"))
    return [opcode] + dir_bytes
# loop
def assemble_loop(addr: int):
    opcode = 0x17
    dir_bytes = list(addr.to_bytes(4, "big"))
    return [opcode] + dir_bytes
# add
def assemble_add(dst, src):
    opcode = 0x09
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]
# sub
def assemble_sub(dst, src):
    opcode = 0x0A
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]
# mul
def assemble_mul(dst, src):
    opcode = 0x0B
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]
# div
def assemble_div(dst, src):
    opcode = 0x0C
    operand = (registers[dst] << 4) | registers[src]
    return [opcode, operand]
# ret
def assemble_ret():
    opcode = 0x8
    return [opcode]
# ensambla una linea
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

    elif instr == "inc":
        return assemble_inc(parts[1].split(",")[0])
    
    elif instr == "dec":
        return assemble_dec(parts[1].split(",")[0])

    elif instr == "mov":
        prts:list[str] = parts[1].split(",")
        dst = prts[0]
        is_pub_alias = False
        is_pul_alias = False
        if dst.startswith("[byte]"):
            is_pub_alias = True
        elif dst.startswith("[dword]"):
            is_pul_alias = True

        if not is_pub_alias and not is_pul_alias:
            src = None
            if prts.__len__() == 2:
                src = prts[1]
            return assemble_mov(dst, src)
        elif is_pul_alias:
            return assemble_pul(assemble_solve(dst[7:], context))
        else:
            expretion = dst[6:]
            if expretion in registers:
                return assemble_pubr(assemble_solve(dst[6:], context))
            else:
                return assemble_pub(assemble_solve(dst[6:], context))

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
        count = int(assemble_solve(ps[0], context))

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
    elif instr == "cq":
        addr = int(assemble_solve(parts[1].split(",")[0], context)) 
        return assemble_cq(addr)
    elif instr == "cnq":
        addr = int(assemble_solve(parts[1].split(",")[0], context)) 
        return assemble_cnq(addr)
    elif instr == "cg":
        addr = int(assemble_solve(parts[1].split(",")[0], context)) 
        return assemble_cg(addr)
    elif instr == "cng":
        addr = int(assemble_solve(parts[1].split(",")[0], context)) 
        return assemble_cng(addr)
    elif instr == "loop":
        addr = int(assemble_solve(parts[1].split(",")[0], context)) 
        return assemble_loop(addr)

    elif instr == "ret":
        return assemble_ret()
    
    elif instr == "pub":
        ps = parts[1].split(",")   # lista de registros o símbolos
        prs = []

        for name in ps:
            name = name.strip()  # quitar espacios
            if name in registers:
                prs.append(0x014)     # opcode de pubr
                prs.append(registers[name])  # resolver nombre
            else:
                prs.append(0x04)     # opcode de pub
                prs.append(int(assemble_solve(name, context)))  # resolver nombre

        return prs
    elif instr == "pul": # put long
        ps = parts[1]
        value = int(assemble_solve(ps, context))
        return assemble_pul(value)
    elif instr == "db":
        ar = parts[1].split(",")
        name, rest = ar
        direction = None
        if ar.__len__() > 2:
            direction = ar[2]
        size = int(rest)
    
        # Registrar variable en el contexto
        context.add_variable(name, size)

        return []
    
    elif instr == "org":
        ptr = assemble_solve(parts[1], context)
        context.ds_pointer = ptr
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
    
    elif instr == "gul":
        reg = parts[1]
        return assemble_gul(reg)
    elif instr == "iret" or instr == "exit":
        return [0x21]
    elif instr == "int":
        return [0x20, registers[parts[1]]]
    elif instr == "hlt":
        return [0x11]
    elif instr == "sti":
        return [0x12]
    elif instr == "cli":
        return [0x13]
    elif instr == "cmp":
        dst, src = parts[1].split(",")
        return assemble_cmp(dst, src)

    # en el contexto
    elif context.symbols.get(parts[0]) is not None:
        # la variable
        variable = parts[0]
        # la accion
        action = parts[1]
        # el valor
        value = parts[2]
        # en linea
        inline = []

        if action == "mov":
            index = "0"
            # si es mayor
            if parts.__len__() == 4:
                index = parts[3]
            # ivar var,0
            inline += assemble_line("ivar " + variable + ",0", context, len)
            # align 0
            inline += assemble_line("align " + index, context, len)
            # mov [byte]inmediato
            inline += assemble_line("mov " + value, context, len)
            # align 0
            inline += assemble_line("align 0", context, len)
            return inline
        elif action == "add":
            index = "0"
            if parts.__len__() == 4:
                index = parts[3]
            # ivar var,0
            inline += assemble_line(f"ivar {variable},0", context, len)
            # align index
            inline += assemble_line(f"align {index}", context, len)
            # gub a
            inline += assemble_line("gub a", context, len)
            # dec off
            inline += assemble_line("dec off", context, len)
            # mov valor
            inline += assemble_line(f"mov [byte]{value}", context, len)
            # dec off
            inline += assemble_line("dec off", context, len)
            # gub b
            inline += assemble_line("gub b", context, len)
            # add a,b
            inline += assemble_line("add a,b", context, len)
            # align index
            inline += assemble_line(f"align {index}", context, len)
            # mov [byte]a
            inline += assemble_line("mov [byte]a", context, len)
        elif action == "sub":
            index = "0"
            if parts.__len__() == 4:
                index = parts[3]
            # ivar var,0
            inline += assemble_line(f"ivar {variable},0", context, len)
            # align index
            inline += assemble_line(f"align {index}", context, len)
            # gub a
            inline += assemble_line("gub a", context, len)
            # dec off
            inline += assemble_line("dec off", context, len)
            # mov valor
            inline += assemble_line(f"mov [byte]{value}", context, len)
            # dec off
            inline += assemble_line("dec off", context, len)
            # gub b
            inline += assemble_line("gub b", context, len)
            # add a,b
            inline += assemble_line("sub a,b", context, len)
            # align index
            inline += assemble_line(f"align {index}", context, len)
            # mov [byte]a
            inline += assemble_line("mov [byte]a", context, len)
        elif action == "div":
            index = "0"
            if parts.__len__() == 4:
                index = parts[3]
            # ivar var,0
            inline += assemble_line(f"ivar {variable},0", context, len)
            # align index
            inline += assemble_line(f"align {index}", context, len)
            # gub a
            inline += assemble_line("gub a", context, len)
            # dec off
            inline += assemble_line("dec off", context, len)
            # mov valor
            inline += assemble_line(f"mov [byte]{value}", context, len)
            # dec off
            inline += assemble_line("dec off", context, len)
            # gub b
            inline += assemble_line("gub b", context, len)
            # add a,b
            inline += assemble_line("div a,b", context, len)
            # align index
            inline += assemble_line(f"align {index}", context, len)
            # mov [byte]a
            inline += assemble_line("mov [byte]a", context, len)
        elif action == "mul":
            index = "0"
            if parts.__len__() == 4:
                index = parts[3]
            # ivar var,0
            inline += assemble_line(f"ivar {variable},0", context, len)
            # align index
            inline += assemble_line(f"align {index}", context, len)
            # gub a
            inline += assemble_line("gub a", context, len)
            # dec off
            inline += assemble_line("dec off", context, len)
            # mov valor
            inline += assemble_line(f"mov [byte]{value}", context, len)
            # dec off
            inline += assemble_line("dec off", context, len)
            # gub b
            inline += assemble_line("gub b", context, len)
            # add a,b
            inline += assemble_line("mul a,b", context, len)
            # align index
            inline += assemble_line(f"align {index}", context, len)
            # mov [byte]a
            inline += assemble_line("mov [byte]a", context, len)

            return inline
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
        prts:list[str] = parts[1].split(",")
        dst = prts[0]
        is_pub_alias = False
        is_pul_alias = False
        if dst.startswith("[byte]"):
            is_pub_alias = True
        elif dst.startswith("[dword]"):
            is_pul_alias = True

        if not is_pub_alias and not is_pul_alias:
            return 2
        elif is_pul_alias:
            return 5
        else:
            return 2
    elif instr == "cmp":
        return 2
    elif instr == "in":
        return 2
    elif instr == "out":
        return 2
    elif instr == "add":
        return 2
    elif instr == "gub" or instr == "gul":
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
    elif instr == "call" or instr == "loop" or instr == "cq" or instr == "cnq" or instr == "cg" or instr == "cng":
        return 5   # opcode + 4 bytes de dirección
    elif instr == "ret":
        return 1
    elif instr == "inc" or instr == "dec":
        return 2
    elif instr == "pub":
        ps = parts[1].split(",")
        return len(ps) * 2   # cada pub = opcode + operando
    elif instr == "ivar":
        return 6   # opcode + size + 4 bytes addr
    elif instr == "align":
        return 2
    elif instr == "db":
        return 0
    elif instr == "pul":
        return 5
    elif instr == "org":
        return 0
    elif instr == "int":
        return 2
    elif instr == "iret" or instr == "exit":
        return 1
    elif instr == "cli" or instr == "sti" or instr == "hlt":
        return 1

    # en el contexto
    else:
        # la variable
        variable = instr
        # la accion
        action = parts[1]
        # el valor
        value = parts[2]
        # en linea
        inline = 0

        if action == "mov":
            index = "0"
            # si es mayor
            if parts.__len__() == 4:
                index = parts[3]
            # ivar var,0
            inline += instr_length("ivar " + variable + ",0", context)
            # align 0
            inline += instr_length("align " + index, context)
            # mov [byte]inmediato
            inline += instr_length("mov " + value, context)
            # align 0
            inline += instr_length("align 0", context)
            return inline
        elif action == "add":
            index = "0"
            if len(parts) == 4:
                index = parts[3]
            # ivar var,0
            inline += instr_length(f"ivar {variable},0", context)
            # align index
            inline += instr_length(f"align {index}", context)
            # gub a
            inline += instr_length("gub a", context)
            # dec off
            inline += instr_length("dec off", context)
            # mov valor
            inline += instr_length(f"mov {value}", context)
            # dec off
            inline += instr_length("dec off", context)
            # gub b
            inline += instr_length("gub b", context)
            # add a,b
            inline += instr_length("add a,b", context)
            # align index
            inline += instr_length(f"align {index}", context)
            # mov [byte]a
            inline += instr_length("mov [byte]a", context)
        elif action == "sub":
            index = "0"
            if len(parts) == 4:
                index = parts[3]
            # ivar var,0
            inline += instr_length(f"ivar {variable},0", context)
            # align index
            inline += instr_length(f"align {index}", context)
            # gub a
            inline += instr_length("gub a", context)
            # dec off
            inline += instr_length("dec off", context)
            # mov valor
            inline += instr_length(f"mov {value}", context)
            # dec off
            inline += instr_length("dec off", context)
            # gub b
            inline += instr_length("gub b", context)
            # add a,b
            inline += instr_length("sub a,b", context)
            # align index
            inline += instr_length(f"align {index}", context)
            # mov [byte]a
            inline += instr_length("mov [byte]a", context)
        elif action == "div":
            index = "0"
            if len(parts) == 4:
                index = parts[3]
            # ivar var,0
            inline += instr_length(f"ivar {variable},0", context)
            # align index
            inline += instr_length(f"align {index}", context)
            # gub a
            inline += instr_length("gub a", context)
            # dec off
            inline += instr_length("dec off", context)
            # mov valor
            inline += instr_length(f"mov {value}", context)
            # dec off
            inline += instr_length("dec off", context)
            # gub b
            inline += instr_length("gub b", context)
            # add a,b
            inline += instr_length("div a,b", context)
            # align index
            inline += instr_length(f"align {index}", context)
            # mov [byte]a
            inline += instr_length("mov [byte]a", context)
        elif action == "mul":
            index = "0"
            if len(parts) == 4:
                index = parts[3]
            # ivar var,0
            inline += instr_length(f"ivar {variable},0", context)
            # align index
            inline += instr_length(f"align {index}", context)
            # gub a
            inline += instr_length("gub a", context)
            # dec off
            inline += instr_length("dec off", context)
            # mov valor
            inline += instr_length(f"mov {value}", context)
            # dec off
            inline += instr_length("dec off", context)
            # gub b
            inline += instr_length("gub b", context)
            # add a,b
            inline += instr_length("mul a,b", context)
            # align index
            inline += instr_length(f"align {index}", context)
            # mov [byte]a
            inline += instr_length("mov [byte]a", context)

            print(inline)
            return inline
