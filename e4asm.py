# importa el ensamblador
from e4lib.assambler import e4asm
# importa el sistema
import sys

# princiapl
def main():
    # el argumento 1
    file_name = sys.argv[1]
    # abrirlo
    with open(file_name, "r") as file:
        # ensamblar el programa
        program = e4asm.CompileCode(file.read())
    
    # Guardar binario
    out_name = sys.argv[2]
    # abrirlo
    with open(out_name, "wb") as out:
        # escribirlo
        out.write(bytes(program))

    # notificar
    print("Programa ensamblado en:", out_name)

# si es el main
if __name__ == "__main__":
    # ejecutar el main
    main()