import e4lib.e4c.parser as e4c
import sys

def main():
    file_name = sys.argv[1]
    file_result = sys.argv[2]

    program = ""
    with open(file_name, "r") as file:
        program = e4c.e4c_parser.parse_code(file.read())
    with open(file_result, "w") as out:
        out.write(program)
  
if __name__ == "__main__":
    main()