# importar el contexto
from e4lib.e4asm.context import e4asm_context as AssemblerContext
# importar los registros
from e4lib.e4asm.registers import e4asm_registers as registers
# importar el resolvedor de lineas y el medidor de instrucciones
from e4lib.e4asm.line import assemble_line, instr_length

# el solve
assemble_solve = AssemblerContext.assemble_solve

# el ensamblador
class e4asm:
    # compila un codigo
    @staticmethod
    def CompileCode(code:str):
        # contenido
        content = code.replace("\r", "\n").split("\n")
        # contexto
        context = AssemblerContext()

        # pc
        pc = 0
        # recorrer lineas
        for line in content:
            # partes
            parts = line.split(";")[0].strip().split()
            # si no hay partes continuar
            if not parts: continue
            # instruccion
            instr = parts[0].lower()
            # si es una funcion
            if instr == "label":
                # nombre
                name = parts[1].split(",")[0]
                # añadir
                context.symbols[name] = pc
            else:
                # calcula tamaño de instrucción para avanzar pc
                pc += instr_length(line, context)

        # Segunda pasada: ensamblar
        program = []
        # program counter
        pc = 0
        # las lineas
        for line in content:
            # bytes de la instruccion
            instr_bytes = assemble_line(line, context, pc)
            # programa
            program += instr_bytes
            # longitud
            pc += len(instr_bytes)

        # donde termina
        print("memory ends at: ", context.ds_pointer)
        return bytes(program)

# alias para versiones antiguas
assamble_code = e4asm.CompileCode