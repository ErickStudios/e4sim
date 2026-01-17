# el tipo de memoria
from e4lib.e4arch.mementry import e4arch_mementry as entry
# el mapa de memoria
memmap:list[str, entry] = {
    # display
    "display": entry(0xBB2, 0x1BB2)
}