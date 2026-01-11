# tipo de hardware
class e4arch_hardware:
    # inicializa
    def __init__(self, update, disconnect, io_in=None, io_out=None):
        # actualizacion de hardware
        self.update = update
        # desconectar
        self.disconnect = disconnect
        # input
        self.input = io_in
        # outpud
        self.outpud = io_out