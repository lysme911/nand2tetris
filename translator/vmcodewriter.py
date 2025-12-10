# vmcodewriter.py

class CodeWriter:

    def __init__(self, file_out_path: str):
        self.arth_jump_flag = 0
        self.out = open(file_out_path, "w", encoding="utf-8")

    def writeArithmetic(self, command: str):

        if command == "add":
            self.out.write(self._arithmetic_template1() + "M=M+D\n")

        elif command == "sub":
            self.out.write(self._arithmetic_template1() + "M=M-D\n")

        elif command == "and":
            self.out.write(self._arithmetic_template1() + "M=M&D\n")

        elif command == "or":
            self.out.write(self._arithmetic_template1() + "M=M|D\n")

        elif command == "gt":
            self.out.write(self._arithmetic_template2("JLE"))  # not <=
            self.arth_jump_flag += 1

        elif command == "lt":
            self.out.write(self._arithmetic_template2("JGE"))  # not >=
            self.arth_jump_flag += 1

        elif command == "eq":
            self.out.write(self._arithmetic_template2("JNE"))  # not <>
            self.arth_jump_flag += 1

        elif command == "not":
            self.out.write("@SP\nA=M-1\nM=!M\n")

        elif command == "neg":
            self.out.write("D=0\n@SP\nA=M-1\nM=D-M\n")

        else:
            raise ValueError("Call writeArithmetic() for a non-arithmetic command")

    def writePushPop(self, command: int, segment: str, index: int):

        from vmparser import Parser  

        if command == Parser.PUSH:
            if segment == "constant":
                self.out.write(
                    f"@{index}\n"
                    "D=A\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )

            elif segment == "local":
                self.out.write(self._push_template1("LCL", index, is_direct=False))

            elif segment == "argument":
                self.out.write(self._push_template1("ARG", index, is_direct=False))

            elif segment == "this":
                self.out.write(self._push_template1("THIS", index, is_direct=False))

            elif segment == "that":
                self.out.write(self._push_template1("THAT", index, is_direct=False))

            elif segment == "temp":
                self.out.write(self._push_template1("R5", index + 5, is_direct=False))

            elif segment == "pointer" and index == 0:
                self.out.write(self._push_template1("THIS", index, is_direct=True))

            elif segment == "pointer" and index == 1:
                self.out.write(self._push_template1("THAT", index, is_direct=True))

            elif segment == "static":
                self.out.write(self._push_template1(str(16 + index), index, is_direct=True))

            else:
                raise ValueError("Unknown segment in PUSH")

        elif command == Parser.POP:
            if segment == "local":
                self.out.write(self._pop_template1("LCL", index, is_direct=False))

            elif segment == "argument":
                self.out.write(self._pop_template1("ARG", index, is_direct=False))

            elif segment == "this":
                self.out.write(self._pop_template1("THIS", index, is_direct=False))

            elif segment == "that":
                self.out.write(self._pop_template1("THAT", index, is_direct=False))

            elif segment == "temp":
                self.out.write(self._pop_template1("R5", index + 5, is_direct=False))

            elif segment == "pointer" and index == 0:
                self.out.write(self._pop_template1("THIS", index, is_direct=True))

            elif segment == "pointer" and index == 1:
                self.out.write(self._pop_template1("THAT", index, is_direct=True))

            elif segment == "static":
                self.out.write(self._pop_template1(str(16 + index), index, is_direct=True))

            else:
                raise ValueError("Unknown segment in POP")

        else:
            raise ValueError("Call writePushPop() for a non-pushpop command")

    def close(self):
        if self.out:
            self.out.close()

    # ------------------ private helper methods ------------------

    def _arithmetic_template1(self) -> str:

        return (
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"
            "A=A-1\n"
        )

    def _arithmetic_template2(self, jump_type: str) -> str:
        
        flag = self.arth_jump_flag
        return (
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"
            "A=A-1\n"
            "D=M-D\n"
            f"@FALSE{flag}\n"
            f"D;{jump_type}\n"
            "@SP\n"
            "A=M-1\n"
            "M=-1\n"
            f"@CONTINUE{flag}\n"
            "0;JMP\n"
            f"(FALSE{flag})\n"
            "@SP\n"
            "A=M-1\n"
            "M=0\n"
            f"(CONTINUE{flag})\n"
        )

    def _push_template1(self, segment: str, index: int, is_direct: bool) -> str:
       
        if is_direct:
            no_pointer_code = ""
        else:
            no_pointer_code = f"@{index}\nA=D+A\nD=M\n"

        return (
            f"@{segment}\n"
            "D=M\n"
            f"{no_pointer_code}"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )

    def _pop_template1(self, segment: str, index: int, is_direct: bool) -> str:
       
        if is_direct:
            no_pointer_code = "D=A\n"
            
        else:
            no_pointer_code = f"D=M\n@{index}\nD=D+A\n"

        return (
            f"@{segment}\n"
            f"{no_pointer_code}"
            "@R13\n"
            "M=D\n"
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"
            "@R13\n"
            "A=M\n"
            "M=D\n"
        )
