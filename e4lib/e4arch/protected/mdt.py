# clase de datos
from dataclasses import dataclass
# self
from typing import Self
# entrada
@dataclass
class e4arch_MDTEntry:
    # base
    base: int
    # tamaño
    size: int
    # acceso (0x43=kernel, 0x21=user+)
    access: int
    # desde memoria
    @staticmethod
    def from_memory(mem: bytearray, offset: int) -> Self:
        # leer 4 bytes para base
        base = int.from_bytes(mem[offset:offset+4], "little")
        # leer 4 bytes para size
        size = int.from_bytes(mem[offset+4:offset+8], "little")
        # leer 1 byte para access
        access = mem[offset+8]
        # retornarlo
        return Self(base, size, access)