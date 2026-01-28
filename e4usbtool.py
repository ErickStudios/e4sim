# usbtool.py
import sys
# importar fs
from e4lib.e4fs.fs import e4fs
# importar el fs2
from e4lib.e4fs.fsb import e4fs_fs2

def create_new2_img(usb_img_file, bootsector_executable_file):
    # leer el archivo del boot sector
    with open(bootsector_executable_file, "rb") as f:
        data = f.read()

    # crear un bloque de 512 bytes
    usb_img_bootsector = e4fs_fs2.new_partition(data, 100,100)
    # añadir bytes de prueba
    test_bytes = bytearray()

    # unir todo en la imagen USB
    usb_img = usb_img_bootsector + test_bytes

    # guardar
    with open(usb_img_file, "wb") as f:
        f.write(usb_img)

    print(f"Imagen USB creada: {usb_img_file}")
    print(f"Tamaño total: {len(usb_img)} bytes")

def create_new_img(usb_img_file, bootsector_executable_file):
    # leer el archivo del boot sector
    with open(bootsector_executable_file, "rb") as f:
        data = f.read()

    # crear un bloque de 512 bytes
    usb_img_bootsector = e4fs.new_partition(data)
    # añadir bytes de prueba
    test_bytes = bytearray()

    # unir todo en la imagen USB
    usb_img = usb_img_bootsector + test_bytes

    # guardar
    with open(usb_img_file, "wb") as f:
        f.write(usb_img)

    print(f"Imagen USB creada: {usb_img_file}")
    print(f"Tamaño total: {len(usb_img)} bytes")

def copy_file_to_img(usb_img_file, file_to_copy, name_in):
    # leer archivo a copiar
    with open(file_to_copy, "rb") as f:
        content = f.read()
    # crear estructura e4fs
    file_entry = e4fs.newfile(name_in, bytearray(content))
    # guardar en .img
    with open(usb_img_file, "ab") as f:
        f.write(file_entry)
    print(f"Archivo {file_to_copy} copiado a imagen {usb_img_file}")

def coppy2_file_to_img(usb_img_file, file_to_copy, name_in:str):
    # leer archivo a copiar
    with open(file_to_copy, "rb") as f:
        content = f.read()
    # crear estructura e4fs
    file_entry = e4fs_fs2.add_file(
        open(usb_img_file, "rb").read(), 
        name_in.encode("utf-8"),
        bytearray(content)
        )
    # guardar en .img
    with open(usb_img_file, "wb") as f:
        f.write(file_entry)
    print(f"Archivo {file_to_copy} copiado a imagen {usb_img_file}")

if __name__ == "__main__":
    mode = sys.argv[1]

    if mode == "-new":
        usb_img_file = sys.argv[2]
        bootsector_executable_file = sys.argv[3]
        create_new_img(usb_img_file, bootsector_executable_file)
    
    elif mode == "-new2":
        usb_img_file = sys.argv[2]
        bootsector_executable_file = sys.argv[3]
        create_new2_img(usb_img_file, bootsector_executable_file)

    elif mode == "-cpy":
        usb_img_file = sys.argv[2]
        file_to_copy = sys.argv[3]
        file_name = sys.argv[4]
        copy_file_to_img(usb_img_file, file_to_copy, file_name)

    elif mode == "-cpy2":
        usb_img_file = sys.argv[2]
        file_to_copy = sys.argv[3]
        file_name = sys.argv[4]
        coppy2_file_to_img(usb_img_file, file_to_copy, file_name)

    else:
        print("Uso:")
        print("  usbtool.py -new <usb_img_file> <bootsector_executable_file>")
        print("  usbtool.py -cpy <usb_img_file> <file_to_copy>")