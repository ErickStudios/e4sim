# usbtool.py
import sys

class e4fs:
    def __init__(self):
        pass

    def newfile(self, path: str, content: bytearray) -> bytearray:
        file = bytearray()
        file += len(path).to_bytes(4, "big")
        file += path.encode("utf-8")
        file += len(content).to_bytes(4, "big")
        file += content
        return file

def create_new_img(usb_img_file, bootsector_executable_file):
    # leer el archivo del boot sector
    with open(bootsector_executable_file, "rb") as f:
        data = f.read()

    # crear un bloque de 512 bytes
    usb_img_bootsector = bytearray(512)
    usb_img_bootsector[:len(data)] = data[:512]

    # añadir bytes de prueba
    test_bytes = bytearray()

    # unir todo en la imagen USB
    usb_img = usb_img_bootsector + test_bytes

    # guardar
    with open(usb_img_file, "wb") as f:
        f.write(usb_img)

    print(f"Imagen USB creada: {usb_img_file}")
    print(f"Tamaño total: {len(usb_img)} bytes")

def copy_file_to_img(usb_img_file, file_to_copy):
    fs = e4fs()
    # leer archivo a copiar
    with open(file_to_copy, "rb") as f:
        content = f.read()
    # crear estructura e4fs
    file_entry = fs.newfile(file_to_copy, bytearray(content))
    # guardar en .img
    with open(usb_img_file, "ab") as f:
        f.write(file_entry)
    print(f"Archivo {file_to_copy} copiado a imagen {usb_img_file}")

if __name__ == "__main__":
    mode = sys.argv[1]

    if mode == "-new":
        usb_img_file = sys.argv[2]
        bootsector_executable_file = sys.argv[3]
        create_new_img(usb_img_file, bootsector_executable_file)

    elif mode == "-cpy":
        usb_img_file = sys.argv[2]
        file_to_copy = sys.argv[3]
        copy_file_to_img(usb_img_file, file_to_copy)

    else:
        print("Uso:")
        print("  usbtool.py -new <usb_img_file> <bootsector_executable_file>")
        print("  usbtool.py -cpy <usb_img_file> <file_to_copy>")