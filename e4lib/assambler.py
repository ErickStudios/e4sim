# importar el contexto
from e4lib.e4asm.context import e4asm_context as AssemblerContext
# importar los registros
from e4lib.e4asm.registers import e4asm_registers as registers
# importar el resolvedor de lineas y el medidor de instrucciones
import e4lib.e4asm.line as e4lib_line
# importar modulos
from e4lib.e4asm.module import search_module
# importar regex
import re

# alias
assemble_line = e4lib_line.assemble_line
instr_length = e4lib_line.instr_length

# el solve
assemble_solve = AssemblerContext.assemble_solve

# el ensamblador
class e4asm:
    # compila un codigo
    @staticmethod
    def CompileCode(code:str, context:(AssemblerContext | None)=None, lenof=0):
        # contenido
        content = code.replace("\r", "\n").split("\n")
        # contexto
        context = AssemblerContext() if not context else context

        # haciendo una estructura?
        stru_make = False
        stru_name = ""
        stru_fields:list[tuple[str, str]] = []
        stru_obligatory_fields:list[str] = []
        stru_allow_subclass = False

        trait_make = False
        trait_name = ""
        trait_dependences:list[str] = []

        # pc
        pc = lenof
        # recorrer lineas
        for line in content:
            # partes
            parts = line.split(";")[0].strip().split()
            # si no hay partes continuar
            if not parts: continue

            match_stru = re.match(r"\.(\w+)\s+db\s+(.+)", line.split(";")[0].strip())
            if (match_stru and stru_make) and (not stru_allow_subclass):
                name, size = match_stru.group(1), match_stru.group(2)
                stru_fields.append((name, size))
                continue

            match_stru = re.match(r"imps\s+stru\s+(\w+)", line.split(";")[0].strip())
            if (match_stru and stru_make) and (stru_allow_subclass):
                name = match_stru.group(1)
                stru_fields += context.structs[name]
                continue

            match_stru_trait_imp = re.match(r"imps\s+trait\s+(\w+)", line.split(";")[0].strip())
            if (match_stru_trait_imp and stru_make):
                name = match_stru_trait_imp.group(1)
                stru_obligatory_fields += context.traits[name]
                continue

            match_trait_field = re.match(r"needs\s+(\w+)", line.split(";")[0].strip())
            if (match_trait_field and trait_make) :
                name = match_trait_field.group(1)
                trait_dependences.append(name)
                continue

            # en estructura
            if (line.split(";")[0].strip() == "}") and stru_make:
                stru_pact_obligatory_fields = True

                for field in stru_obligatory_fields:
                    field_content = False
                    for field_real in stru_fields:
                        if field_real[0] == field:
                            field_content = True
                            break
                    if not field_content:
                        print("error " + stru_name + " needs to implement " + field)
                        stru_pact_obligatory_fields = False
                        break
                if stru_pact_obligatory_fields:
                    context.structs[stru_name] = stru_fields[:]
                    stru_make = False
                continue

            # en traits
            if (line.split(";")[0].strip() == "}") and trait_make:
                context.traits[trait_name] = trait_dependences[:]
                trait_make = False
                continue

            # instruccion
            instr = parts[0].lower()
            # si es una funcion
            if instr == "label":
                # nombre
                name = parts[1].split(",")[0]
                # añadir
                context.symbols[name] = pc
            # si es un trait
            elif instr == "trait":
                # nombre
                name = parts[1]
                # trait activada
                if (parts[2] is not None and parts[2].strip() == '{'):
                    # hacerlo
                    trait_make = True
                    # nombre
                    trait_name = name
                    # dependencias
                    trait_dependences = []
            # si es un stru
            elif instr == "stru":
                # nombre
                name = parts[1]
                # estructura activada
                if (parts[2] is not None and parts[2].strip() == '{'):
                    # hacerlo
                    stru_make = True
                    # nombre
                    stru_name = name
                    # estructuras
                    stru_fields = []
                    # si es una stru
                    stru_allow_subclass = False
                    # campos obligatorios
                    stru_obligatory_fields = []
            # si es un imp
            elif instr == "imp" and line.split(";")[0].strip().endswith("{"):
                # nombre
                name = parts[1]
                # estructura activada
                if (parts[2] is not None and parts[2].strip() == '{'):
                    # hacerlo
                    stru_make = True
                    # nombre
                    stru_name = name
                    # estructuras
                    stru_fields = []
                    # si es una imp
                    stru_allow_subclass = True
                    # campos obligatorios
                    stru_obligatory_fields = []
            else:
                # calcula tamaño de instrucción para avanzar pc
                pc += instr_length(line, context, pc)

        # Segunda pasada: ensamblar
        program = []
        # program counter
        pc = lenof
        # las lineas
        for line in content:
            # bytes de la instruccion
            instr_bytes = assemble_line(line, context, pc)
            # programa
            program += instr_bytes
            # longitud
            pc += len(instr_bytes)

        # donde termina
        return bytes(program)

# alias para versiones antiguas
assamble_code = e4asm.CompileCode
# setear
e4lib_line.e4lib_modules.set_solve_code_a(assamble_code)