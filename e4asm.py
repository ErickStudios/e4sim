import e4lib.assambler as e4asm
import sys

def main():
    context = e4asm.AssemblerContext()

    file_name = sys.argv[1]
    with open(file_name, "r") as file:
        program = e4asm.assamble_code(file.read())
    
    # Guardar binario
    out_name = sys.argv[2]
    with open(out_name, "wb") as out:
        out.write(bytes(program))

    print("Programa ensamblado en:", out_name)

if __name__ == "__main__":
    main()