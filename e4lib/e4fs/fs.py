# e4fs
class e4fs:
    # inicializa
    def __init__(self):
        pass
    # nueva particion/fs
    @staticmethod
    def new_partition(executable_bootsector: bytes):
        # sector de 512 bytes inicializado en cero
        partition = bytearray(512)

        # tamaño
        size_hdr = 16                               # tamaño
        fs_name = b"e4fs".ljust(8, b' ')            # el nombre del fs
        oem_name = b"ErCrSt".ljust(7, b' ')         # nombre del fabricante del pendrive

        # escribir header
        partition[0] = size_hdr                     # tamaño
        partition[1:1+8] = fs_name                  # nombre fs
        partition[9:9+7] = oem_name                 # nombre fabricante

        # inicio
        start_code = size_hdr
        # escribir particion
        partition[start_code:start_code+len(executable_bootsector)] = executable_bootsector[:512-size_hdr]

        return partition
    # nuevo archivo
    @staticmethod
    def newfile(path: str, content: bytearray) -> bytearray:
        # el archivo
        file = bytearray()
        # adjuntarlo
        file += (
            # el tamaño de el directorio
            len(path).to_bytes(4, "big")            + 
            # el directorio
            path.encode("utf-8")                    + 
            # longitud
            len(content).to_bytes(4, "big")         + 
            content
        )
        return file
    # nuevo archivo
    @staticmethod
    def e4file_create(path:str, content:bytearray) -> bytearray: 
        return e4fs.newfile(path, content)