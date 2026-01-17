# random
from random import randrange
# la direccion lan
class lan_addr:
    # el init
    def __init__(self, add1d, add2d, add3d, add4d):
        # direccion
        self.address = [ add1d, add2d, add3d, add4d ]
# la clase
class e4hardware_eic3045:
    # el init
    def __init__(self):
        # inicializar
        self.init_eic3045()
    # inicializa la red
    def init_eic3045(self):
        # iniciar
        self.direction = lan_addr(
            randrange(0, 255), 
            randrange(0, 255), 
            randrange(0, 255), 
            randrange(0, 255)
        )
        # abrir archivo en modo lectura/escritura binaria 
        self.file = open("lan.bin", "w+b")
        # la base addr
        self.base_addr = 0xC000
    # mandar a lan
    def lan_send(self, data:int):
        # mover puntero al inicio
        self.file.seek(0)
        network = bytearray(self.file.read())
        network.append(data)
        # reescribir desde el inicio
        self.file.seek(0)
        self.file.write(network)
        self.file.flush()
    # recivir
    def lan_recive(self) -> int:
        # mover puntero al inicio
        self.file.seek(0)
        network = bytearray(self.file.read())
        if not network:
            return 0    # nada que leer
        data = network[0]
        # quitar primer elemento
        network = network[1:]
        # reescribir desde el inicio
        self.file.seek(0)
        self.file.write(network)
        self.file.flush()
        return data