# regex
import re
# tipos
from e4lib.e4c.types import e4c_type_size
# estructura
class e4c_struct:
    # inicializa
    def __init__(self, structsolve: str, types: dict[str, e4c_type_size]):
        # el original
        self.original = {}
        # los offsets
        self.offsets: dict[str, int] = {}
        # el tamaño total
        self.total_size = 0
        # parsear
        self._parse(structsolve, types)
    # para acceder
    @staticmethod
    def set_struct_field(context, struct_name:str, field:str, value:str, RegisterUse:str=None):
        # estructura
        struct:e4c_struct = context.structures.get(context.struct_vars.get(struct_name))
        # tamaño
        field_size:int = struct.original[field]
        # la directiva que se usara
        directive = "mov [byte]"
        # si es estandar
        if RegisterUse is None:
            # si se usa 4 bytes
            if field_size == 4:
                # directiva de valor literal
                directive = "mov [dword]"
        # si usa registros
        else:
            # usa directiva normal
            directive = "mov [byte]"
            # si se usa 4 bytes
            if field_size == 4:
                # directiva
                directive = "mov "
        # codigo
        code = ";; e4c: struct access\nivar " + struct_name + ",0 ;; e4c: struct variable\nalign " + str(struct.offsets.get(field)) + ";; e4c: offset\n" + directive + (RegisterUse if RegisterUse is not None else value) + "\n"
        # retornar
        return code
    # para acceder
    @staticmethod
    def get_struct_field(context, struct_name:str, field:str, register:str):
        # estructura
        struct:e4c_struct = context.structures.get(context.struct_vars.get(struct_name))
        # tamaño
        field_size:int = struct.original[field]
        # la directiva que se usara
        directive = "gub "
        # si se usa 4 bytes
        if field_size == 4:
            # directiva de valor literal
            directive = "gul "
        # codigo
        code = ";; e4c: struct access\nivar " + struct_name + ",0 ;; e4c: struct variable\nalign " + str(struct.offsets.get(field)) + ";; e4c: offset\n" + directive + register + "\n"
        # retornar
        return code
    # para parsear
    def _parse(self, structsolve: str, types: dict[str, e4c_type_size]):
        # quitar llaves y comentarios
        body = re.findall(r"{([^}]*)}", structsolve, re.S)
        # si no esta el cuerpo
        if not body:
            # no hacer nada
            return
        # las lineas
        lines = body[0].split(";")
        # el offset
        offset = 0
        # recorrer lineas
        for line in lines:
            # trimear la linea
            line = line.strip()
            # si no hay linea
            if not line:
                # continuar
                continue
            # partes
            parts = line.split()
            # tipo y nombre
            tipo, nombre = parts[0], parts[1]
            # tamaño
            size = (types.get(tipo, 0)).value
            # el original
            self.original[nombre] = size
            # el offset
            self.offsets[nombre] = offset
            # aumentarlo
            offset += size
        # tamaño total
        self.total_size = offset
