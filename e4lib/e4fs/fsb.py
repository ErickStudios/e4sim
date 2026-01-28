# el tiempo
import time
# clase
class e4fs_struct:
    # el para generar una estructura
    @staticmethod
    def gn_struct(
        nam:str,
        ptr_content:int,
        date_crt:int,
        date_edit:int,
        size_content:int
    ) -> bytearray:
        # estructura
        struct = bytearray()
        # añadir nombre
        struct = struct + (
            len(nam).to_bytes(4, "big")             + 
            nam.encode("utf-8")
            )
        # añadir fechas
        struct = struct + (
            date_crt.to_bytes(4, "big") +
            date_edit.to_bytes(4, "big") 
        )
        # el puntero y tamaño del contenido
        struct = struct + (
            size_content.to_bytes(4, "big") +
            ptr_content.to_bytes(4, "big")
            )
        # retornarlo
        return struct
# el e4fs2
class e4fs_fs2:
    # nueva particion
    @staticmethod
    def new_partition(
        executable_bootsector: bytes, 
        table_size:int, 
        data_size:int
        ) -> bytearray:
        partition = bytearray(512)

        size_hdr = 16
        fs_name = b"e4fs2".ljust(8, b' ')
        oem_name = b"ErCrSt".ljust(7, b' ')

        # header
        partition[0] = size_hdr
        partition[1:1+8] = fs_name
        partition[9:9+7] = oem_name

        # bootsector
        start_code = size_hdr
        partition[start_code:start_code+len(executable_bootsector)] = executable_bootsector[:512-size_hdr]

        # offsets
        base = 512
        table_offset = base + 8   # después de escribir table_size y data_size
        data_offset  = table_offset + table_size

        # escribir tamaños
        partition += table_size.to_bytes(4, "big")
        partition += data_size.to_bytes(4, "big")

        # punteros iniciales
        partition += table_offset.to_bytes(4, "big")   # end_files_entry
        partition += data_offset.to_bytes(4, "big")    # end_contents_entry

        # reservar tabla y datos
        partition += bytearray(table_size)
        partition += bytearray(data_size)

        return partition    # añade un archivo a una particion
    @staticmethod
    def add_file(
        part: bytearray, 
        filename: bytes, 
        content: bytes
        ):
        # el retval
        part_new = bytearray(part[:])
        # offsets
        array_files_end_entry = [ 0x208, 0x20C ]
        array_contents_entry_end = [ 0x20C, 0x210 ]
        # calcular el fin de archivos
        end_files_entry = int.from_bytes(part[0x208:0x20C], "big")
        end_contents_entry = int.from_bytes(part[0x20C:0x210], "big")
        # el archivo
        entry = e4fs_struct.gn_struct(str(filename), end_contents_entry, int(time.time()), int(time.time()), len(content))
        # escribir contenido
        part_new[end_files_entry:end_files_entry+len(entry)] = entry
        # escribir contenido
        part_new[end_contents_entry:end_contents_entry+len(content)] = content
        # actualizar punteros en el header
        new_end_files = end_files_entry + len(entry)
        new_end_contents = end_contents_entry + len(content)
        # actualizar
        part_new[0x208:0x20C] = new_end_files.to_bytes(4, "big")
        part_new[0x20C:0x210] = new_end_contents.to_bytes(4, "big")
        # retornar
        return part_new