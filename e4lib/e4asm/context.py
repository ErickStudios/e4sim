# importar registros
from e4lib.e4asm.registers import e4asm_registers as registers
# contexto de ensamblado
class e4asm_context:
    # inicializar
    def __init__(self):
        # Diccionario de símbolos: nombre -> dirección
        self.symbols = {}
        # Puntero actual del segmento de datos (ds)
        self.ds_pointer = 0x00000000
    # añadir variable
    def add_variable(self, name, size, direction=None):
        # si la direccion es none
        if direction is None:
            # Guardar variable en la tabla de símbolos
            self.symbols[name] = self.ds_pointer
            # Avanzar el puntero del segmento de datos
            self.ds_pointer += size
        # si no
        else:
            # setear direccion manualmente
            self.symbols[name] = direction
            # retornar el simbolo
        return self.symbols[name]
    # obtiene direccion
    def get_address(self, name):
        # Obtener dirección de una variable
        return self.symbols.get(name, None)
    # resuelve algo
    @staticmethod
    def assemble_solve(syntax: str, context):
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
