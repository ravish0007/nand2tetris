from symbol_table import ClassSymbolType, SubroutineSymbolType

kind_to_segment = {
    ClassSymbolType.STATIC: "static",
    ClassSymbolType.FIELD: "this",
    SubroutineSymbolType.ARG: "argument",
    SubroutineSymbolType.VAR: "local",
}


class VMWriter:
    def __init__(self, outputpath):
        self.outputfile = open(outputpath, "w")

    def writeLines(self, lines):
        for line in lines:
            self.outputfile.write(f"{line}\n")

    def write_if(self, label):
        self.writeLines(["not", f"if-goto {label}"])

    def write_goto(self, label):
        self.writeLines([f"goto {label}"])

    def write_label(self, label):
        self.writeLines([f"label {label}"])

    def write_function(self, jack_subroutine):
        class_name = jack_subroutine.jack_class.class_name
        function_name = jack_subroutine.name
        vars_count = jack_subroutine.var_symbols_count

        self.writeLines([f"function {class_name}.{function_name} {vars_count}"])

    def write_return(self):
        self.writeLines(["return"])

    def write_call(self, class_name, func_name, arg_count):
        self.writeLines([f"call {class_name}.{func_name} {arg_count}"])

    def write_pop_symbol(self, jack_symbol):
        kind, _, offset = jack_symbol
        segment = kind_to_segment[kind]

        self.write_pop(segment, offset)

    def write_push_symbol(self, jack_symbol):
        kind, _, offset = jack_symbol
        segment = kind_to_segment[kind]
        self.write_push(segment, offset)

    def write_pop(self, segment, offset):
        self.writeLines([f"pop {segment} {offset}"])

    def write_push(self, segment, offset):
        self.writeLines([f"push {segment} {offset}"])

    def write(self, action):
        self.writeLines([f"{action}"])

    def write_int(self, n):
        self.write_push("constant", n)

    def write_string(self, string):
        # s = s[1:-1]
        self.write_int(len(string))
        self.write_call("String", "new", 1)
        for char in string:
            self.write_int(ord(char))
            self.write_call("String", "appendChar", 2)

    def write_arithmetic(self, operator, is_unary=False):
        vm_commands = {
            "+": "add",
            ("-", True): "neg",
            ("-", False): "sub",
            ("~", True): "not",
            "*": "call Math.multiply 2",
            "/": "call Math.divide 2",
            "&": "and",
            "|": "or",
            "<": "lt",
            ">": "gt",
            "=": "eq",
        }

        if operator in "-~":
            self.writeLines([vm_commands[(operator, is_unary)]])
        else:
            self.writeLines([vm_commands[operator]])

    def close(self):
        self.outputfile.close()
