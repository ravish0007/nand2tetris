def generate_assembly_output(tip, commands):
    return "\n".join([f"// {tip}", *commands, "", ""])


def generate_end():
    return generate_assembly_output("reached end", ["(FIN)", "@FIN", "0;JMP"])


def generate_unary_arithmetic(type):
    operation_type = {"neg": "M=-M", "not": "M=!M"}
    commands = ["@SP", "A=M-1", operation_type[type]]
    return generate_assembly_output(type, commands)


def generate_binary_arithmetic(type):
    operation_type = {"add": "M=D+M", "sub": "M=M-D", "or": "M=D|M", "and": "M=D&M"}
    commands = ["@SP", "AM=M-1", "D=M", "@SP", "A=M-1", operation_type[type]]
    return generate_assembly_output(type, commands)


def generate_comparision(type, label):
    operation_type = {"eq": "D;JEQ", "lt": "D;JLT", "gt": "D;JGT"}
    commands = [
        "@SP",
        "AM=M-1",
        "D=M",
        "@SP",
        "A=M-1",
        "D=M-D",
        f"@jumptrue{label}",
        operation_type[type],
        "D=0",
        f"@jumpfalse{label}",
        "0;JMP",
        f"(jumptrue{label})",
        "D=-1",
        f"(jumpfalse{label})",
        "@SP",
        "A=M-1",
        "M=D",
    ]
    return generate_assembly_output(type, commands)


def generate_push(segment, index, label):
    location_mapping = {
        "this": "THIS",
        "that": "THAT",
        "argument": "ARG",
        "local": "LCL",
        "pointer": "3",
        "temp": "5",
    }

    address_memory = {"temp": "D=A", "pointer": "D=A", "rest": "D=M"}

    push_type = {
        "static": [f"@{label}.{index}", "D=M"],
        "constant": [f"@{index}", "D=A"],
        "rest": [
            f'@{location_mapping.get(segment, "ERRRORRRR")}',
            f'{address_memory.get(segment, address_memory["rest"])}',
            f"@{index}",
            "A=D+A",
            "D=M",
        ],
    }
    commands = [
        *push_type.get(segment, push_type["rest"]),
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ]
    return generate_assembly_output(segment, commands)


def generate_pop(segment, index, label):

    if segment == "static":
        return generate_assembly_output(
            f"pop {segment} {index}",
            ["@SP", "AM=M-1", "D=M", f"@{label}.{index}", "M=D"],
        )

    location_mapping = {
        "this": "THIS",
        "that": "THAT",
        "argument": "ARG",
        "local": "LCL",
        "pointer": "3",
        "temp": "5",
    }

    address_memory = {"temp": "D=A", "pointer": "D=A", "rest": "D=M"}

    commands = [
        f"@{location_mapping[segment]}",
        f'{address_memory.get(segment, address_memory["rest"])}',
        f"@{index}",
        "D=D+A",
        "@R13",
        "M=D",
        "@SP",
        "AM=M-1",
        "D=M",
        "@R13",
        "A=M",
        "M=D",
    ]

    return generate_assembly_output(f"pop {segment} {index}", commands)


def generate_label(label):
    commands = [f"({label})"]
    return generate_assembly_output(f"label {label}", commands)


def generate_goto(label):
    commands = [f"@{label}", "0;JMP"]
    return generate_assembly_output(f"goto {label}", commands)


def generate_if(label):
    commands = ["@SP", "AM=M-1", "D=M", f"@{label}", "D;JNE"]
    return generate_assembly_output(f"if-goto {label}", commands)


def generate_function(name, args):
    commands = [f"({name})", *["@SP", "A=M", "M=0", "@SP", "M=M+1"] * args]
    return generate_assembly_output(f"function {name} {args}", commands)


def generate_call(name, args, return_label):
    push_return_address = [
        f"@{return_label}",
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ]
    commands = [*push_return_address]

    for segment in ["@LCL", "@ARG", "@THIS", "@THAT"]:
        # commands.extend(["", segment, "D=M", "@SP", "A=M", "D=M", "@SP", "M=M+1", ""])
        commands.extend(["", segment, "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1", ""])

    position_arg = ["@SP", "D=M", "@5", "D=D-A", f"@{args}", "D=D-A", "@ARG", "M=D"]

    position_local = ["@SP", "D=M", "@LCL", "M=D"]

    function_call = [
        f"@{name}",
        "0;JMP",
    ]

    commands.extend(position_arg)
    commands.extend(position_local)
    commands.extend(function_call)
    commands.append(f"({return_label})")

    return generate_assembly_output(f"call {name} {args}", commands)


def generate_return():

    save_local = [
        "@LCL",
        "D=M",
        "@R13",
        "M=D",
    ]

    save_return_address = ["@R13", "D=M", "@5", "A=D-A", "D=M", "@R14", "M=D"]
    position_return_value = ["@SP", "AM=M-1", "D=M", "@ARG", "A=M", "M=D"]
    positon_sp = ["@ARG", "D=M+1", "@SP", "M=D"]
    restore_that = ["@R13", "D=M", "@1", "A=D-A", "D=M", "@THAT", "M=D"]
    restore_this = ["@R13", "D=M", "@2", "A=D-A", "D=M", "@THIS", "M=D"]
    restore_arg = ["@R13", "D=M", "@3", "A=D-A", "D=M", "@ARG", "M=D"]
    resote_local = ["@R13", "D=M", "@4", "A=D-A", "D=M", "@LCL", "M=D"]
    jump_to_address = ["@R14", "A=M", "0;JMP"]

    return generate_assembly_output(
        "return",
        [
            *save_local,
            *save_return_address,
            *position_return_value,
            *positon_sp,
            *restore_that,
            *restore_this,
            *restore_arg,
            *resote_local,
            *jump_to_address,
        ],
    )


class CodeWriter:
    def __init__(self, output):
        self.static_label = output
        self.file = open(output + ".asm", "w")
        self.label = 0
        self.calls = 0
        self.current_function = ""

    def close(self):
        self.file.close()

    def writeArithmetic(self, command):
        if command in {"add", "sub", "or", "and"}:
            self.file.write(generate_binary_arithmetic(command))
        elif command in {"neg", "not"}:
            self.file.write(generate_unary_arithmetic(command))
        elif command in {"eq", "gt", "lt"}:
            self.file.write(generate_comparision(command, self.label))
            self.label += 1

    def setFileName(self, name):
        self.static_label = name

    def bootstrap(self):
        self.file.write(
            generate_assembly_output(
                "bootstrap",
                # ["@256", "D=A", "@SP", "M=D", "@Sys.init", "0;JMP"],
                # "bootstrap",
                ["@256", "D=A", "@SP", "M=D"],
            )
        )

        self.file.write(generate_call("Sys.init", 0, "bootstrap"))

    def writePushPop(self, command_type, segment, index):
        if command_type == "push":
            self.file.write(generate_push(segment, index, self.static_label))
        elif command_type == "pop":
            self.file.write(generate_pop(segment, index, self.static_label))

    def writeLabel(self, label):
        self.file.write(generate_label(f"{self.current_function}${label}"))

    def writeGoto(self, label):
        self.file.write(generate_goto(f"{self.current_function}${label}"))

    def writeIf(self, label):
        self.file.write(generate_if(f"{self.current_function}${label}"))

    def writeFunction(self, function_name, n_args):
        self.current_function = function_name
        self.file.write(generate_function(function_name, int(n_args)))

    def writeCall(self, function_name, n_args):
        return_label = f"{self.current_function}$ret.{self.calls}"
        self.calls += 1
        self.file.write(generate_call(function_name, int(n_args), return_label))

    def writeReturn(self):
        self.file.write(generate_return())

    def writeEnd(self):
        self.file.write(generate_end())
