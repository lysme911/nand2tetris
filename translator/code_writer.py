# vmcodewriter.py

class CodeWriter:
    """
    Translates VM commands into Hack assembly code.
    """

    def __init__(self, file_out_path: str):
        self.arth_jump_flag = 0
        self.out = open(file_out_path, "w", encoding="utf-8")
        print(f"[CodeWriter] Open output: {file_out_path}")

    def writeArithmetic(self, command: str):
        """
        Write the assembly code that is the translation of the given arithmetic command.
        command: 'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'
        """
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
        """
        Write the assembly code that is the translation of the given command
        where the command is either PUSH or POP.

        command: 例如 Parser.PUSH 或 Parser.POP（你在 Parser 裡應該會定義常數）
        segment: 'constant', 'local', 'argument', 'this', 'that', 'temp', 'pointer', 'static'
        index:   整數 index
        """
        from vmparser import Parser  # 假設你有一個 Parser 類別定義 PUSH/POP 常數

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
                # 注意：這裡沿用你原本 Java 的邏輯，R5 + (index+5)
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
        """
        Close the output file.
        """
        print("[CodeWriter] Closing output file")
        if self.out:
            self.out.close()

    # ------------------ private helper methods ------------------

    def _arithmetic_template1(self) -> str:
        """
        Template for add, sub, and, or:
        把兩個 stack top 取出，D = 第二個，A-1 是第一個，最後在 M 上運算。
        """
        return (
            "@SP\n"
            "AM=M-1\n"
            "D=M\n"
            "A=A-1\n"
        )

    def _arithmetic_template2(self, jump_type: str) -> str:
        """
        Template for gt, lt, eq.
        jump_type: 'JLE', 'JGE', 'JNE' 之類
        """
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
        """
        Template for push local/argument/this/that/temp/pointer/static
        segment:   LCL / ARG / THIS / THAT / R5 / '16+index' 等
        index:     對應的 index
        is_direct: True 時表示 segment 本身就是要讀的位址（pointer/static）
        """
        # pointer / static：直接讀該位址
        # 其餘：先從 segment 得到 base，再 + index
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
        """
        Template for pop local/argument/this/that/temp/pointer/static
        segment:   LCL / ARG / THIS / THAT / R5 / '16+index' 等
        index:     對應的 index
        is_direct: True 時表示 segment 本身就是目標位址（pointer/static）
        """
        if is_direct:
            # pointer / static：segment 直接是位址
            no_pointer_code = "D=A\n"
        else:
            # 先取得 segment 中的 base 再 + index
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
