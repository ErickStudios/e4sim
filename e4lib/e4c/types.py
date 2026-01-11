# enums
from enum import Enum
# tipo
class e4c_type_size(Enum):
    # el int8 es un byte
    IntUint8 = 1
    # el int 16 no existe se redondea a 32
    IntUint16 = 4
    # es el estandar
    IntUint32 = 4
    # solo permite byte y dword
    IntUint64 = 4