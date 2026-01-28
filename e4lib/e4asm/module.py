# tipos
from typing import TYPE_CHECKING
# el os
import os
# el glob
import glob
# el self
from typing import Self
# hacerlo
from e4lib.e4asm.context import e4asm_context
# solve
solve_code_a = None
# solve set
def set_solve_code_a(val): 
    global solve_code_a
    solve_code_a = val
# para modulos
class e4asm_module:
    # inicializa
    def __init__(self):
        self.macros:dict[str, str] = {}
    # para expansion de macros
    @staticmethod
    def ParseMacros(code: str) -> dict[str, str]:
        macros = {}
        lines = code.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line.startswith("@RegexDef"):
                regex = line.replace("@RegexDef", "").strip()
                i += 1
                if i < len(lines) and lines[i].strip() == "@impl_begins":
                    i += 1
                    expansion_lines = []
                    while i < len(lines) and lines[i].strip() != "@impl_ends":
                        expansion_lines.append(lines[i])
                        i += 1
                    macros[regex] = "\n".join(expansion_lines)
            i += 1
        return macros
    # desde un preprocesado
    def from_file(code:str) -> Self:
        # nuevo modulo
        self = e4asm_module()
        # abrirlo
        self.macros = e4asm_module.ParseMacros(code)
        # retornarlo
        return self
# alias
e4asm_modules = e4asm_module
# añade
def search_namespace(namespace: str, as_what: str) -> dict[str, str]:
    ns_path = "." + os.sep + namespace.replace(".", os.sep)
    full_path = ns_path

    modules: dict[str, str] = {}

    for modfile in glob.glob(os.path.join(full_path, "mod.*.e4asm")):
        # nombre del archivo sin ruta
        filename = os.path.basename(modfile)              
        # quitar prefijo "mod." y sufijo ".e4asm"
        alias = as_what + "." + filename.removeprefix("mod.").removesuffix(".e4asm")

        # guardar en el diccionario
        modules[alias] = modfile

    return modules
# para buscar un modulo cerca
def search_module(name: str, glob_file: dict[str, str], len_of:int, context:e4asm_context=e4asm_context()) -> (e4asm_module | tuple[bytes, e4asm_context]):
    # si el alias existe en glob_file, usar esa ruta
    if name in glob_file:
        modpath = glob_file[name]
        with open(modpath, "r", encoding="utf-8") as f:
            readed = f.read()
            if readed.startswith("@module_executable"):
                readed = readed[len("@module_executable"):]
                code = solve_code_a(readed, context,len_of)
                return (code, activated)
            return e4asm_module.from_file(readed)

    # si no existe, buscar en la carpeta actual
    path = os.path.dirname(__file__)
    modpath = os.path.join(path, f"mod.{name}.e4asm")
    with open(modpath, "r") as f:
        readed = f.read()
        if readed.startswith("@module_executable"):
            activated = e4asm_context()
            readed = readed[len("@module_executable"):]
            code = solve_code_a(readed, context)
            return (code, activated)
        return e4asm_module.from_file(f.read())
