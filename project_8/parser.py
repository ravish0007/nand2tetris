from enum import Enum


class Command(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8
    C_END = 9


class Parser:
    arithmetic_commands = {"sub", "add", "neg", "eq", "gt", "lt", "and", "or", "not"}
    command_types = {
        "push": Command.C_PUSH,
        "pop": Command.C_POP,
        "call": Command.C_CALL,
        "goto": Command.C_GOTO,
        "if-goto": Command.C_IF,
        "label": Command.C_LABEL,
        "function": Command.C_FUNCTION,
        "return": Command.C_RETURN,
        "none": Command.C_END,
    }

    def __init__(self, input):
        self.file = open(input)
        self.command = []

    def hasMoreLines(self):
        previous_location = self.file.tell()
        status = self.file.readline() != ""
        self.file.seek(previous_location)
        return status

    def advance(self):
        command_found = False
        while not command_found:
            line = self.file.readline().strip()

            if line == "":
                self.command = ["none"]
                break

            line = line.strip()

            if line.startswith("//") or not line:
                continue

            if line.find("//") > 0:
                line = line[: line.index("//")]

            command_found = True
            self.command = line.split(" ")

    def commandType(self):
        command = self.command[0]

        if not command:
            raise Exception("Command not found")

        if command in Parser.arithmetic_commands:
            return Command.C_ARITHMETIC

        return Parser.command_types[command]

    def arg1(self):
        if len(self.command) != 0:
            if self.commandType() == Command.C_ARITHMETIC:
                return self.command[0]
            return self.command[1]
        raise Exception("Command buffer is empty")

    def arg2(self):
        if len(self.command) > 1:
            return self.command[2]
        raise Exception("Command buffer is empty")
