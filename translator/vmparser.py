# vmparser.py

class Parser:
    ARITHMETIC = 0
    PUSH = 1
    POP = 2
    LABEL = 3
    GOTO = 4
    IF = 5
    FUNCTION = 6
    RETURN = 7
    CALL = 8

    arithmeticCmds = {
        "add", "sub", "neg",
        "eq", "gt", "lt",
        "and", "or", "not"
    }

    def __init__(self, file_in_path: str):
        self.argType = -1
        self.argument1 = ""
        self.argument2 = -1

        try:
            with open(file_in_path, "r", encoding="utf-8") as f:
                preprocessed_lines = []
                for line in f:
                    line = self.noComments(line).strip()
                    if len(line) > 0:
                        preprocessed_lines.append(line)

            self.lines = preprocessed_lines
            self.current_index = -1
            self.currentCmd = None


        except FileNotFoundError:
            print("File not found:", file_in_path)
            self.lines = []
            self.current_index = -1
            self.currentCmd = None

    def hasMoreCommands(self) -> bool:
        return self.current_index + 1 < len(self.lines)

    def advance(self):
        if not self.hasMoreCommands():
            raise StopIteration("No more commands")

        self.current_index += 1
        self.currentCmd = self.lines[self.current_index]

        self.argument1 = ""
        self.argument2 = -1
        self.argType = -1

        segs = self.currentCmd.split()

        if len(segs) > 3:
            raise ValueError(f"Too many arguments in: {self.currentCmd}")

        if segs[0] in self.arithmeticCmds:
            self.argType = self.ARITHMETIC
            self.argument1 = segs[0]

        elif segs[0] == "return":
            self.argType = self.RETURN
            self.argument1 = segs[0]

        else:
            if len(segs) < 2:
                raise ValueError(f"Missing argument1 in: {self.currentCmd}")

            self.argument1 = segs[1]
            cmd = segs[0]

            if cmd == "push":
                self.argType = self.PUSH
            elif cmd == "pop":
                self.argType = self.POP
            elif cmd == "label":
                self.argType = self.LABEL
            elif cmd == "if-goto" or cmd == "if":
                self.argType = self.IF
            elif cmd == "goto":
                self.argType = self.GOTO
            elif cmd == "function":
                self.argType = self.FUNCTION
            elif cmd == "call":
                self.argType = self.CALL
            else:
                raise ValueError(f"Unknown command type in: {self.currentCmd}")

            if self.argType in (self.PUSH, self.POP, self.FUNCTION, self.CALL):
                if len(segs) < 3:
                    raise ValueError(f"Missing argument2 in: {self.currentCmd}")
                try:
                    self.argument2 = int(segs[2])
                except ValueError:
                    raise ValueError(f"Argument2 is not an integer in: {self.currentCmd}")

    def commandType(self) -> int:
        if self.argType != -1:
            return self.argType
        else:
            raise RuntimeError("No current command. Did you call advance()?")

    def arg1(self) -> str:
        if self.commandType() != self.RETURN:
            return self.argument1
        else:
            raise RuntimeError("Cannot get arg1 from a RETURN type command!")

    def arg2(self) -> int:
        if self.commandType() in (self.PUSH, self.POP, self.FUNCTION, self.CALL):
            return self.argument2
        else:
            raise RuntimeError("Cannot get arg2 for this command type!")

    @staticmethod
    def noComments(strIn: str) -> str:
        position = strIn.find("//")
        if position != -1:
            strIn = strIn[:position]
        return strIn
