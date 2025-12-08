# vmtranslator.py

import sys
import os
from vmparser import Parser
from code_writer import CodeWriter


def get_vm_files(dir_path: str):
    result = []
    for name in os.listdir(dir_path):
        full_path = os.path.join(dir_path, name)
        if os.path.isfile(full_path) and name.endswith(".vm"):
            result.append(full_path)
    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: python vmtranslator.py [filename|directory]")
        return

    in_path = sys.argv[1]

    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Path not found: {in_path}")

    vm_files = []
    out_path = ""

    if os.path.isfile(in_path):
        if not in_path.endswith(".vm"):
            raise ValueError(".vm file is required!")

        vm_files.append(in_path)
        base, _ = os.path.splitext(os.path.abspath(in_path))
        out_path = base + ".asm"

    elif os.path.isdir(in_path):
        vm_files = get_vm_files(in_path)
        if len(vm_files) == 0:
            raise ValueError("No .vm file in this directory")

        abs_dir = os.path.abspath(in_path)
        dirname = os.path.basename(abs_dir)
        out_path = os.path.join(abs_dir, dirname + ".asm")

    else:
        raise ValueError("Argument must be a file or directory")

    print(f"[Main] Input VM files: {vm_files}")
    print(f"[Main] Output ASM path: {out_path}")

    writer = CodeWriter(out_path)

    total_cmds = 0

    for vm_file in vm_files:
        print(f"[Main] Translating {vm_file}")
        parser = Parser(vm_file)

        while parser.hasMoreCommands():
            parser.advance()
            ctype = parser.commandType()
            total_cmds += 1

            if ctype == Parser.ARITHMETIC:
                writer.writeArithmetic(parser.arg1())
            elif ctype in (Parser.PUSH, Parser.POP):
                writer.writePushPop(ctype, parser.arg1(), parser.arg2())
            else:
                # Project7：其它型別先略過，之後做 Project8 再補
                pass

    writer.close()
    print(f"[Main] Done. Total VM commands processed: {total_cmds}")
    print("File created:", out_path)


if __name__ == "__main__":
    main()
