# tipos
from e4lib.e4c.types import e4c_type_size
# estructuras
from e4lib.e4c.struct import e4c_struct
# contexto
class e4c_context:
    # inicializacion
    def __init__(self):
        # los tipos
        self.types:dict[str, e4c_type_size] = dict()
        # las estructuras
        self.structures:dict[str, e4c_struct] = dict()
        # las estructuras implementadas
        self.struct_vars:dict[str, str] = dict()
        # los arrays
        self.arrays:dict[str, e4c_type_size] = dict()
        # las variables
        self.variables:dict[str, e4c_type_size] = dict()