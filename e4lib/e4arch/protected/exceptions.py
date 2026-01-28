# excepciones
class e4arch_exception:
    # __init__
    # 
    # al lanzarse se ejecuta la excepcion
    # 
    def __init__(self, exceptionName:str , pmode:bool=False):
        self.ex_name = exceptionName
        self.__launch__()
    # la lanza
    def __launch__(self):
        print("#" + self.short_alias)
        # sale de la aplicacion esto apaga la pc
        exit(0)                                 # salir